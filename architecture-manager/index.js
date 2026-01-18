#!/usr/bin/env node
const { McpServer } = require("@modelcontextprotocol/sdk/server/mcp.js");
const { StdioServerTransport } = require("@modelcontextprotocol/sdk/server/stdio.js");
const { z } = require("zod");
const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

const server = new McpServer({
  name: "Architecture-Manager",
  version: "2.0.0",
});

const {
  validateInputs,
  runCommand,
  initDualPhaseQueue,
  popNextRequirement,
  transitionTaskState,
  registerInterfaceItem,
  updateRequirementArtifacts,
  startService,
  killProcessOnPort
} = require('./utils.js');


// --- Init ---
server.tool(
  "init_project",
  "Initialize Agile Development Queue and Git Repository (if missing).",
  {
    project_root: z.string().describe("MANDATORY. Project root path."),
  },
  async (args) => {
    const validationError = validateInputs(args);
    if (validationError) return { content: [{ type: "text", text: validationError }] };
    
    try {
      const result = initDualPhaseQueue(args);
      
      // Handle errors or messages returned from utils
      if (result.error) {
         return { content: [{ type: "text", text: `Error: ${result.error}` }] };
      }

      // Check and init git if needed
      const { project_root } = args;
      const gitPath = path.join(project_root, '.git');

      if (!fs.existsSync(gitPath)) {
        await runCommand('git init', project_root);
        await runCommand('git add .', project_root);
        await runCommand('git commit -m "init"', project_root);
      }

      return { content: [{ type: "text", text: result.message }] };
    } catch (err) {
      return { content: [{ type: "text", text: `Error: ${err.message}` }] };
    }
  }
);

// --- Pop Next Requirement ---
server.tool(
  "pop_next_requirement",
  "Get next TDD task. Returns next requirement to be processed, either RED (Design) or GREEN (Implementation) phase.",
  { project_root: z.string() },
  async (args) => {
    const validationError = validateInputs(args);
    if (validationError) return { content: [{ type: "text", text: validationError }] };
    const { project_root } = args;

    try {
      const result = await popNextRequirement(project_root, 'progress.yaml', path.join(project_root, 'docs', 'requirements'));
      
      if (result.error) return { content: [{ type: "text", text: result.error }] };
      
      return { content: [{ type: "text", text: result.formattedOutput }] };
    } catch (err) { 
      return { content: [{ type: "text", text: `Error: ${err.message}` }] };
    }
  }
);

// --- Unified Register Interface Tool ---
server.tool(
  "register_interface",
  "Unified interface registration tool. Registers UI components, API endpoints, or backend functions to a central interface registry. [Type: UI | API | FUNC]",
  {
    project_root: z.string().describe("Absolute path to the project root directory"),
    type: z.enum(["UI", "API", "FUNC"]).describe("Interface type: UI (Frontend), API (Backend Route), FUNC (Backend Logic)"),
    id: z.string().describe("Unique identifier ID for the interface (e.g., UI-LOGIN-FORM, API-AUTH-LOGIN)"),
    path: z.string().describe("Relative path to the file"),
    related_req_id: z.string().describe("Associated requirement ID"),
    description: z.string().optional().describe("Description (UI/General)"),
    signature: z.string().optional().describe("Function signature or API method path (API/FUNC)"),
    upstream_ids: z.array(z.string()).optional().describe("List of upstream dependency IDs (who calls me)"),
    downstream_ids: z.array(z.string()).optional().describe("List of downstream dependency IDs (who do I call) - UI/API only"),
    db_tables: z.array(z.string()).optional().describe("Database table names involved - FUNC only"),
  },
  async (args) => {
    // 1. Basic validation
    const validationError = validateInputs(args);
    if (validationError) return { content: [{ type: "text", text: validationError }] };

    const { project_root, type, id, related_req_id, path, ...data } = args;
    
    // 2. Configure strategies
    const strategies = {
      UI: {
        artifactField: 'ui_ids',
        validMergeFields: ['upstream_ids', 'downstream_ids'],
        storeData: { description: data.description, path } 
      },
      API: {
        artifactField: 'api_ids',
        validMergeFields: ['upstream_ids', 'downstream_ids'],
        storeData: { signature: data.signature, path }
      },
      FUNC: {
        artifactField: 'func_ids',
        validMergeFields: ['upstream_ids', 'db_tables'],
        storeData: { signature: data.signature, path }
      }
    };

    const strategy = strategies[type];
    if (!strategy) {
      return { content: [{ type: "text", text: `Error: Unknown interface type ${type}` }] };
    }

    try {
      // 3. Execute registration logic
      const itemData = { 
        type, 
        related_req_id, 
        ...strategy.storeData,
        ...data 
      };

      registerInterfaceItem(
        project_root, 
        id, 
        itemData, 
        strategy.validMergeFields
      );

      // 4. Update requirement association
      if (related_req_id) {
        updateRequirementArtifacts(
          project_root, 
          related_req_id, 
          strategy.artifactField, 
          id
        );
      }

      return { content: [{ type: "text", text: `Success: Registered ${type} node [${id}]` }] };
    } catch (err) {
      console.error(err);
      return { content: [{ type: "text", text: `Error registering ${type}: ${err.message}` }] };
    }
  }
);

// --- Save Progress (Commit) ---
server.tool(
  "save_progress",
  "Commit code AND complete current phase (RED->GREEN or GREEN->DONE). Run ONLY when tests match expectations.",
  {
    project_root: z.string(),
    message: z.string().describe("Commit message"),
    current_task_id: z.string().describe("The ID of the requirement you just worked on (e.g. REQ-5-2)"),
  },
  async (args) => {
    const { project_root, message, current_task_id } = args;

    try {
      // 1. State Transition
      const transition = transitionTaskState(project_root, current_task_id);
      
      // 2. Git Commit
      const addRes = await runCommand('git add .', project_root);
      const commitRes = await runCommand(`git commit -m "${message}"`, project_root);

      const info = `[State Change] ${current_task_id}: ${transition.prev} -> ${transition.current}`;
      return { content: [{ type: "text", text: `Success: ${message}\n${info}` }] };

    } catch (err) {
      return { content: [{ type: "text", text: `Error: ${err.message}` }] };
    }
  }
);

// --- Start Services Tool ---
server.tool(
  "start_dev_server",
  "Start Frontend (5173) and Backend (8000) servers in background modes for E2E testing.",
  {
    project_root: z.string().describe("MANDATORY. Project root path."),
  },
  async (args) => {
    const { project_root } = args;
    const feDir = path.join(project_root, 'frontend');
    const beDir = path.join(project_root, 'backend');

    try {
      killProcessOnPort(8000);
      killProcessOnPort(5173);

      await startService(beDir, "Backend");
      await startService(feDir, "Frontend");

      return { 
        content: [{ 
          type: "text", 
          text: `Services Started.\n- Frontend: http://localhost:5173\n- Backend: http://localhost:8000\n\nYou can now run Playwright tests against these URLs.` 
        }] 
      };
    } catch (err) {
      return { content: [{ type: "text", text: `Error starting services: ${err.message}` }] };
    }
  }
);

// --- Stop Services Tool ---
server.tool(
  "stop_dev_server",
  "Stop Frontend and Backend servers by killing processes on ports 8000 and 5173.",
  {},
  async (args) => {
    try {
      killProcessOnPort(8000);
      killProcessOnPort(5173);
      return { content: [{ type: "text", text: "Services Stopped (Ports 8000 & 5173 released)." }] };
    } catch (err) {
      return { content: [{ type: "text", text: `Error stopping services: ${err.message}` }] };
    }
  }
);

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  process.exit(1);
});
