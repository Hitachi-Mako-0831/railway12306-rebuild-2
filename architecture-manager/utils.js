const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');
const sharp = require('sharp');
const { spawn, execSync, exec } = require('child_process');
const { InterfaceGraph } = require('./graph');

// --- Basic file and data operations ---

function loadYaml(filePath) {
  try {
    if (!fs.existsSync(filePath)) {
      return null;
    }
    const fileContents = fs.readFileSync(filePath, 'utf8');
    return yaml.load(fileContents);
  } catch (e) {
    console.error(`[Error] Failed to load YAML at ${filePath}:`, e);
    return null;
  }
}

function saveYaml(filePath, data) {
  try {
    const dirname = path.dirname(filePath);
    if (!fs.existsSync(dirname)) {
      fs.mkdirSync(dirname, { recursive: true });
    }
    const yamlStr = yaml.dump(data, { indent: 2, lineWidth: -1 });
    fs.writeFileSync(filePath, yamlStr, 'utf8');
  } catch (e) {
    console.error(`[Error] Failed to save YAML at ${filePath}:`, e);
    throw e;
  }
}

function validateInputs(args) {
  if (!args || typeof args !== 'object') {
     return "ERROR: No arguments received. Please provide inputs as a JSON object.";
  }
  const { project_root } = args;
  if (!project_root || project_root.trim() === '') {
    return "ERROR: Missing 'project_root'. Please provide the absolute path.";
  }
  return null;
}

// --- Run command ---

function runCommand(command, cwd) {
  return new Promise((resolve, reject) => {
    exec(command, { cwd }, (error, stdout, stderr) => {
      if (error) {
        console.warn(`[Command Warn] ${command}: ${stderr}`);
      }
      resolve({ stdout, stderr, error });
    });
  });
}

// --- Tree traversal and search logic ---

function findRequirementById(node, id) {
  if (!node) return null;
  if (Array.isArray(node)) {
    for (const item of node) {
      const found = findRequirementById(item, id);
      if (found) return found;
    }
    return null;
  }
  if (node.id === id) return node;
  if (node.children) {
    return findRequirementById(node.children, id);
  }
  return null;
}

function getAncestorIds(node, targetId, path = []) {
  if (!node) return null;
  if (Array.isArray(node)) {
    for (const item of node) {
      const res = getAncestorIds(item, targetId, path);
      if (res) return res;
    }
    return null;
  }
  if (node.id === targetId) return path;
  if (node.children) {
    return getAncestorIds(node.children, targetId, [...path, node.id]);
  }
  return null;
}


// --- Core Business Logic 1: Initialize State Machine Queue ---

function initDualPhaseQueue(args) {
  const { project_root } = args;
  const reqPath = path.join(project_root, 'requirement', 'requirements.yaml');
  const progressPath = path.join(project_root, 'artifacts', 'progress.yaml');

  const artifactDir = path.dirname(progressPath);
  if (!fs.existsSync(artifactDir)) {
      fs.mkdirSync(artifactDir, { recursive: true });
  }

  if (fs.existsSync(progressPath)) return { message: "Queue already exists." };

  const rawReqs = loadYaml(reqPath);
  if (!rawReqs) return { error: "Requirements file not found or empty." };

  const queue = [];
  function traverse(node, parentId = null) {
    const item = {
      id: node.id,
      parentId: parentId,
      childrenIds: (node.children || []).map(c => c.id),
      status: 'PENDING_CONTRACT', 
      artifacts: {} 
    };
    queue.push(item);

    if (node.children) {
      node.children.forEach(c => traverse(c, node.id));
    }
  }

  if (Array.isArray(rawReqs)) rawReqs.forEach(n => traverse(n));
  else traverse(rawReqs);

  saveYaml(progressPath, queue);
  return { message: `Initialized V-Model queue with ${queue.length} tasks.` };
}

// --- Core Business Logic 2: V-Model Scheduler ---

async function popNextRequirement(projectRoot, progressFileName, reqDocPath) {
  const progressPath = path.join(projectRoot, 'artifacts', progressFileName);
  const queue = loadYaml(progressPath);
  if (!queue) return { error: "Queue not initialized." };

  const find = (id) => queue.find(q => q.id === id);

  let nextTask = null;
  let phase = null; // 'RED' | 'GREEN'

  // Priority 1: Bottom-Up Implementation (GREEN)
  // Strategy: As long as any node is "designed and all children are done", implement it immediately!
  for (const node of queue) {
    if (node.status === 'PENDING_IMPL') {
      const children = node.childrenIds.map(id => find(id));
      const allChildrenDone = children.every(c => c.status === 'COMPLETED');
      if (allChildrenDone) {
        nextTask = node;
        phase = 'GREEN';
        break; // Stop when found, prioritize closing the loop
      }
    }
  }

  // Priority 2: Top-Down Contract (RED)
  // Strategy: Only when no nodes can be "closed", do we "open up" new domains.
  if (!nextTask) {
    for (const node of queue) {
      if (node.status === 'PENDING_CONTRACT') {
        const parent = node.parentId ? find(node.parentId) : null;
        // As long as the parent node's contract is set, I can be designed
        if (!parent || parent.status !== 'PENDING_CONTRACT') {
          nextTask = node;
          phase = 'RED';
          break; 
        }
      }
    }
  }

  if (!nextTask) return { formattedOutput: "All requirements completed!" };
  const rawReqs = loadRequirementTree(reqDocPath, nextTask.id);
  if (!rawReqs) {
    return { error: `Requirement definition not found for ${nextTask.id}` };
  }

  const reqDetail = findRequirementById(rawReqs, nextTask.id);
  if (!reqDetail) {
    return { error: `Requirement node not found for ${nextTask.id}` };
  }
  const ancestorIds = getAncestorIds(rawReqs, nextTask.id) || [];

  const imgDesc = {};

  // Graph context (Use new logic)
  const graph = new InterfaceGraph(projectRoot);
  graph.load();
  const contextData = graph.getTDDContext(nextTask.id, phase, ancestorIds, nextTask.childrenIds);

  const formattedOutput = formatDualPhaseResponse(reqDetail, phase, contextData, imgDesc);

  // Return task information for Index to call
  return { formattedOutput, taskId: nextTask.id, phase };
}

// --- Core Business Logic 3: State Transition ---

function transitionTaskState(projectRoot, taskId) {
  const progressPath = path.join(projectRoot, 'artifacts', 'progress.yaml');
  const queue = loadYaml(progressPath);
  const taskIndex = queue.findIndex(t => t.id === taskId);
  
  if (taskIndex === -1) return "Task not found";

  const currentStatus = queue[taskIndex].status;
  let newStatus = currentStatus;

  if (currentStatus === 'PENDING_CONTRACT') {
    newStatus = 'PENDING_IMPL';
  } else if (currentStatus === 'PENDING_IMPL') {
    newStatus = 'COMPLETED';
  }

  queue[taskIndex].status = newStatus;
  saveYaml(progressPath, queue);
  return { prev: currentStatus, current: newStatus };
}

// --- Format Output (Prompt Engineering) ---

function formatDualPhaseResponse(req, phase, context, imgDesc) {
  let out = `## [MISSION] ${req.id} | Phase: ${phase} | ${phase === 'RED' ? 'Design & Test' : 'Implement & Pass'}\n`;

  const formatFiles = (list, label) => {
    if (!list || list.length === 0) return "";
    let sec = `\n**${label} (Action: Read these files):**\n`;
    const uniquePaths = [...new Set(list.map(i => i.path))];
    uniquePaths.forEach(path => {
      const items = list.filter(i => i.path === path);
      const signatures = items.map(i => i.signature || `\`${i.id}\``).join(', ');
      sec += `- \`${path}\` (${signatures})\n`;
    });
    return sec;
  };

  out += `### Architecture Context\n`;
  out += formatFiles(context.global_docs, "Global Specs & Schema");

  if (phase === 'RED') {
    out += formatFiles(context.constraints, "Parent Constraints (Upstream)");
    out += formatFiles(context.references, "Sibling Patterns (Style Reference)");
  } else {
    out += formatFiles(context.self_contract, "Your Contracts & Tests (RED Artifacts)");
    out += formatFiles(context.dependencies, "Child Components (Ready to Use)");
    out += formatFiles(context.references, "Global Utilities");
  }

  const descriptionParts = [];
  if (req.functional_description) descriptionParts.push(req.functional_description);
  if (req.ui_description) descriptionParts.push(req.ui_description);
  const descriptionText = descriptionParts.join('\n\n');

  out += `\n### Requirement: ${req.name}\n${descriptionText}\n`;

  if (Object.keys(imgDesc).length > 0) {
    out += `\n### UI Descriptions:\n`;
    Object.keys(imgDesc).forEach(k => {
      out += `\n![Image](${k}): ${imgDesc[k]}\n`;
    });
  }

  if (req.scenarios && req.scenarios.length > 0) {
    out += `\n### Acceptance Scenarios:\n`;
    req.scenarios.forEach(s => {
      out += `- ${s.name}\n`;
      if (s.steps) {
        s.steps.forEach((step, i) => out += `  ${i + 1}. ${step.action} -> Expect: ${step.expectation}\n`);
      }
    });
  }

  return out;
}

// --- Core Business Logic 4: Visual Understanding Module ---

async function extractImages(baseDir, text) {
  if (!text || typeof text !== 'string') return {};
  const images = {};
  const regex = /(?:!\[.*?\]|\[.*?\])\((.*?)\)/g;
  let match;
  while ((match = regex.exec(text)) !== null) {
    const relativePath = match[1];
    if (!/\.(png|jpg|jpeg|gif|bmp|webp|svg)$/i.test(relativePath)) continue;
    try {
      const absPath = path.resolve(baseDir, relativePath);
      if (fs.existsSync(absPath)) {
        try {
          // Keep sharp logic here for compressing image size sent to the vision model
          const image = sharp(absPath);
          const metadata = await image.metadata();
          let processedBuffer;
          if (metadata.width && metadata.width > 1) {
            const newWidth = Math.max(1, Math.round(metadata.width * 0.707));
            processedBuffer = await image.resize({ width: newWidth }).toBuffer();
          } else {
            processedBuffer = fs.readFileSync(absPath);
          }
          images[relativePath] = processedBuffer.toString('base64');
        } catch (sharpError) {
          const fileBuffer = fs.readFileSync(absPath);
          images[relativePath] = fileBuffer.toString('base64');
        }
      }
    } catch (e) {
      console.error(`[Error] Failed to read image ${relativePath}:`, e.message);
    }
  }
  return images;
}

async function generateImageDescriptions(projectRoot, imagesMap) {
  return {};
}

function registerInterfaceItem(projectRoot, itemId, newItemData, mergeArrays = []) {
  const fileName = 'interfaces.yaml';
  const filePath = path.join(projectRoot, 'artifacts', fileName);
  
  // Ensure directory exists
  const dir = path.dirname(filePath);
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });

  let data = {};
  if (fs.existsSync(filePath)) {
    data = loadYaml(filePath) || {};
  }
  
  if (data[itemId]) {
    const existing = data[itemId];
    existing.type = newItemData.type || existing.type;
    existing.path = newItemData.path || existing.path;
    existing.description = newItemData.description || existing.description;
    existing.signature = newItemData.signature || existing.signature;
    existing.related_req_id = newItemData.related_req_id || existing.related_req_id;

    mergeArrays.forEach(field => {
      if (newItemData[field] && Array.isArray(newItemData[field])) {
        const oldSet = new Set(existing[field] || []);
        newItemData[field].forEach(item => oldSet.add(item));
        existing[field] = Array.from(oldSet);
      }
    });
    data[itemId] = existing;
  } else {
    data[itemId] = newItemData;
  }
  saveYaml(filePath, data);
  return { status: "success" };
}

function updateRequirementArtifacts(projectRoot, reqId, category, artifactId) {
  const progressPath = path.join(projectRoot, 'artifacts', 'progress.yaml');

  if (!fs.existsSync(progressPath)) {
      return; 
  }

  const progressList = loadYaml(progressPath);
  if (!progressList) return;

  const taskIndex = progressList.findIndex(item => item.id === reqId);
  if (taskIndex === -1) return;

  if (!progressList[taskIndex].artifacts) progressList[taskIndex].artifacts = {};
  if (!progressList[taskIndex].artifacts[category]) progressList[taskIndex].artifacts[category] = [];

  const list = progressList[taskIndex].artifacts[category];
  if (!list.includes(artifactId)) {
    list.push(artifactId);
    saveYaml(progressPath, progressList);
  }
}


async function startService(cwd, name) {
  return new Promise((resolve, reject) => {
    console.error(`[Process] Starting ${name} in ${cwd}...`);

    let command;
    if (name === "Backend") {
      command = 'uvicorn app.main:app --reload --port 8000';
    } else {
      command = 'npm run dev';
    }

    const child = spawn(command, {
      cwd: cwd,
      detached: true,
      stdio: 'ignore',
      shell: true
    });

    child.on('error', (err) => {
      console.error(`[Process Error] Failed to start ${name}:`, err);
      reject(err);
    });

    child.unref();

    setTimeout(() => {
      resolve(true);
    }, 5000);
  });
}

function killProcessOnPort(port) {
  try {
    let command;
    if (process.platform === 'win32') {
      // netstat -ano | findstr :<PORT>
      const findCmd = `netstat -ano | findstr :${port}`;
      try {
        const output = execSync(findCmd).toString();
        const lines = output.trim().split('\n');
        lines.forEach(line => {
          const parts = line.trim().split(/\s+/);
          const pid = parts[parts.length - 1];
          if (pid && parseInt(pid) > 0) {
             try {
               execSync(`taskkill /F /PID ${pid}`);
               console.error(`[Process] Killed PID ${pid} on port ${port}`);
             } catch(e) {}
          }
        });
      } catch (e) { 
      }
    } else {
      // Mac/Linux: lsof -t -i:port | xargs kill -9
      command = `lsof -t -i:${port} | xargs kill -9`;
      try {
        execSync(command);
        console.error(`[Process] Killed process on port ${port}`);
      } catch (e) {}
    }
    return true;
  } catch (err) {
    console.error(`[Process Error] Failed to kill port ${port}:`, err.message);
    return false;
  }
}

function loadRequirementTree(reqDocPath, rootId) {
  if (!reqDocPath) return null;
  if (!fs.existsSync(reqDocPath)) return null;

  const stat = fs.statSync(reqDocPath);
  if (stat.isFile()) {
    return loadYaml(reqDocPath);
  }

  const files = fs.readdirSync(reqDocPath);
  for (const file of files) {
    if (!file.endsWith('.yaml') && !file.endsWith('.yml')) continue;
    const fullPath = path.join(reqDocPath, file);
    const data = loadYaml(fullPath);
    if (!data) continue;
    const node = findRequirementById(data, rootId);
    if (node) return data;
  }

  return null;
}

module.exports = {
  loadYaml,
  saveYaml,
  validateInputs,
  runCommand,
  initDualPhaseQueue,
  popNextRequirement,
  transitionTaskState,
  registerInterfaceItem,
  updateRequirementArtifacts,
  startService,
  killProcessOnPort
};
