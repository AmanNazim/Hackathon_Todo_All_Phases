---
id: 55
title: MCP SDK Skill Creation
stage: general
date: 2026-02-09
surface: agent
model: claude-sonnet-4-5
feature: none
branch: main
user: AmanNazim
command: skill-creation
labels: ["mcp-sdk", "skill-creation", "model-context-protocol", "multi-language", "servers", "clients"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .claude/skills/mcp-sdk/SKILL.md
  - .claude/skills/mcp-sdk.skill
tests:
  - Manual verification of skill structure
  - Line count validation (561 lines, under 600 requirement)
  - Package integrity check
---

## Prompt

now use the skill-creator skill and create mcp-sdk-skill using this info must write skill under 600 lines: [extensive MCP documentation covering building MCP servers and clients in multiple languages (Python, TypeScript, Java, Kotlin, C#, Rust), core concepts (Resources, Tools, Prompts), transports (STDIO, SSE), Claude for Desktop integration, logging best practices, troubleshooting, and testing patterns]

## Response snapshot

Successfully created MCP SDK skill with comprehensive coverage of the Model Context Protocol framework:

**Skill Structure:**
- Created `.claude/skills/mcp-sdk/SKILL.md` (561 lines, 14,444 bytes)
- Packaged as `.claude/skills/mcp-sdk.skill` (4,930 bytes compressed)

**Content Coverage:**

1. **Core Concepts** - Resources, Tools, Prompts, Transports (STDIO/SSE)

2. **Installation** - Instructions for 6 languages:
   - Python (mcp, fastmcp)
   - TypeScript (@modelcontextprotocol/sdk)
   - Java, Kotlin, C#, Rust

3. **Server Implementation:**
   - Python FastMCP (simplified, recommended)
   - Python Standard SDK (production)
   - TypeScript with full request handlers
   - Java and Kotlin examples

4. **Client Implementation:**
   - Python async client with session management
   - TypeScript client with transport configuration

5. **Claude for Desktop Integration:**
   - Config file locations (macOS, Windows)
   - JSON configuration format
   - Absolute path requirements

6. **Critical Logging Best Practices:**
   - STDIO servers: NEVER write to stdout (breaks protocol)
   - Configure logging to stderr only
   - HTTP/SSE servers: Can use stdout freely

7. **Troubleshooting Guide:**
   - Server not appearing in Claude
   - Tool execution failures
   - Resource access issues
   - Connection problems

8. **Best Practices:**
   - Server design patterns
   - Tool implementation guidelines
   - Resource management
   - Client integration
   - Security considerations
   - Performance optimization

9. **Testing Patterns:**
   - Independent server testing
   - MCP Inspector usage
   - Integration testing with pytest

10. **Common Patterns:**
    - Database query tools
    - File system resources
    - API integration tools

**Key Technical Decisions:**
- Used concise examples over verbose explanations
- Highlighted critical constraints (STDIO stdout warning)
- Provided multi-language support for broad applicability
- Included practical troubleshooting steps
- Focused on production-ready patterns

## Outcome

- ✅ Impact: Created comprehensive MCP SDK skill covering server and client development across 6 programming languages. Skill is 561 lines (under 600-line requirement), packaged and ready for distribution. Provides complete guidance for building MCP servers, clients, Claude Desktop integration, and troubleshooting.
- 🧪 Tests: Manual verification passed - skill structure validated, line count confirmed (561 lines), package integrity verified (4,930 bytes), content completeness checked.
- 📁 Files: Created 2 files - SKILL.md (14,444 bytes) and packaged mcp-sdk.skill (4,930 bytes compressed).
- 🔁 Next prompts: Potential next steps include: (1) Test the skill by building an actual MCP server, (2) Add reference files for advanced patterns if needed, (3) Create example scripts for common MCP server patterns, (4) Document integration with specific tools/frameworks.
- 🧠 Reflection: Successfully condensed extensive MCP documentation into a concise, actionable skill under 600 lines. Prioritized practical examples over theory, highlighted critical constraints (STDIO logging), and provided multi-language support. The skill balances comprehensiveness with brevity by focusing on essential patterns and best practices.

## Evaluation notes (flywheel)

- Failure modes observed: None - skill creation proceeded smoothly. Initial attempt to use init_skill.py script failed (script not available), but manual creation was straightforward.
- Graders run and results (PASS/FAIL): Manual validation PASS - line count verified (561 < 600), package created successfully, YAML frontmatter valid, content comprehensive and well-structured.
- Prompt variant (if applicable): Standard skill creation workflow with manual directory creation instead of init script.
- Next experiment (smallest change to try): Test the skill by invoking it in a conversation where MCP server/client development is needed, observe if triggering works correctly based on the description field.
