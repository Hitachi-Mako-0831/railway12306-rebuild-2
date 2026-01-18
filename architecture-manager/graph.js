const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

class InterfaceGraph {
  constructor(projectRoot) {
    this.projectRoot = projectRoot;
    this.interfaces = {};
    this.graph = { nodes: {}, edges: [] };
  }

  load() {
    const interfacePath = path.join(this.projectRoot, 'artifacts', 'interfaces.yaml');
    try {
      if (fs.existsSync(interfacePath)) {
        const fileContents = fs.readFileSync(interfacePath, 'utf8');
        this.interfaces = yaml.load(fileContents) || {};
      } else {
        this.interfaces = {};
      }
    } catch (e) {
      console.error(`[InterfaceGraph] Failed to load interfaces:`, e);
      this.interfaces = {};
    }
    this.buildGraph();
  }

  buildGraph() {
    this.graph = { nodes: {}, edges: [] };
    // Add nodes
    Object.entries(this.interfaces).forEach(([id, data]) => {
      this.graph.nodes[id] = { id, ...data };
    });

    // Add edges
    Object.values(this.graph.nodes).forEach(node => {
      if (node.downstream_ids) {
        node.downstream_ids.forEach(targetId => this.addEdge(node.id, targetId, 'CALLS'));
      }
      if (node.upstream_ids) {
        node.upstream_ids.forEach(sourceId => this.addEdge(sourceId, node.id, 'CALLS'));
      }
    });
  }

  addEdge(from, to, relation) {
    if (!this.graph.edges.some(e => e.from === from && e.to === to && e.relation === relation)) {
      this.graph.edges.push({ from, to, relation });
    }
  }

  getTDDContext(reqId, phase, ancestorReqIds = [], childReqIds = [], siblingReqIds = []) {
    const context = {
      constraints: [],   // Ancestor constraints
      self_contract: [], // Self contract
      dependencies: [],  // Child dependencies
      references: [],    // Sibling references
      global_docs: []    // Global documents (Metadata, Schema)
    };

    const allInterfaces = Object.values(this.interfaces);
    const findByReq = (rId) => allInterfaces.filter(i => i.related_req_id === rId);

    context.global_docs.push({
      id: 'SYS-METADATA',
      type: 'DOC',
      path: 'metadata.md',
      signature: 'Project Specs, DB Schema, API Registry'
    });

    context.global_docs.push({
      id: 'SYS-DB-INIT',
      type: 'DOC',
      path: 'backend/src/database/init_db.js', 
      signature: 'SQLite DDL Scripts'
    });

    // 1. RED Phase (Design Contract)
    if (phase === 'RED') {
      ancestorReqIds.forEach(pId => {
        context.constraints.push(...findByReq(pId));
      });

      if (siblingReqIds.length > 0) {
        const recentSiblings = siblingReqIds.slice(-3); 
        recentSiblings.forEach(sId => {
           context.references.push(...findByReq(sId));
        });
      }
    }

    // 2. GREEN Phase (Implementation Logic)
    if (phase === 'GREEN') {
      context.self_contract.push(...findByReq(reqId));

      childReqIds.forEach(cId => {
        context.dependencies.push(...findByReq(cId));
      });
    }

    return context;
  }
}

module.exports = { InterfaceGraph };