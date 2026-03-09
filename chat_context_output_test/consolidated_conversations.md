# Consolidated Conversations

## Source 1: C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\api.json

- Characters: 10988

```text
{
 "remote.extensionKind": {
 "ms-azuretools.vscode-cosmosdb": ["ui"],
 "ms-vscode-remote.remote-ssh-edit": ["workspace"]
 }
}
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
 context.subscriptions.push(
 vscode.commands.registerCommand('myAmazingExtension.persistWorkspaceData', async () => {
 if (!context.storageUri) {
 return;
 }

 // Create the extension's workspace storage folder if it doesn't already exist
 try {
 // When folder doesn't exist, and error gets thrown
 await vscode.workspace.fs.stat(context.storageUri);
 } catch {
 // Create the extension's workspace storage folder
 await vscode.workspace.fs.createDirectory(context.storageUri)
 }

 const workspaceData = vscode.Uri.joinPath(context.storageUri, 'workspace-data.json');
 const writeData = new TextEncoder().encode(JSON.stringify({ now: Date.now() }));
 vscode.workspace.fs.writeFile(workspaceData, writeData);
 }
 ));

 context.subscriptions.push(
 vscode.commands.registerCommand('myAmazingExtension.persistGlobalData', async () => {

 if (!context.globalStorageUri) {
 return;
 }

 // Create the extension's global (cross-workspace) folder if it doesn't already exist
 try {
 // When folder doesn't exist, and error gets thrown
 await vscode.workspace.fs.stat(context.globalStorageUri);
 } catch {
 await vscode.workspace.fs.createDirectory(context.globalStorageUri)
 }

 const workspaceData = vscode.Uri.joinPath(context.globalStorageUri, 'global-data.json');
 const writeData = new TextEncoder().encode(JSON.stringify({ now: Date.now() }));
 vscode.workspace.fs.writeFile(workspaceData, writeData);
 ));
}
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
 // ...
 const myApiKey = context.secrets.get('apiKey');
 // ...
 context.secrets.delete('apiKey');
 // ...
 context.secrets.store('apiKey', myApiKey);
}
import * as vscode from 'vscode';

export function activate(context: vscode.ExtensionContext) {
 context.subscriptions.push(vscode.commands.registerCommand('myAmazingExtension.clipboardIt', async () => {
 // Read from clipboard
 const text = await vscode.env.clipboard.readText();

 // Write to clipboard
 await vscode.env.clipboard.writeText(`It looks like you're copying "${text}". Would you like help?`);
 }));
}
import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
 context.subscriptions.push(vscode.commands.registerCommand('myAmazingExtension.openExternal', () => {

 // Example 1 - Open the VS Code homepage in the default browser.
 vscode.env.openExternal(vscode.Uri.parse('https://code.visualstudio.com'));

 // Example 2 - Open an auto-forwarded localhost HTTP server.
 vscode.env.openExternal(vscode.Uri.parse('http://localhost:3000'));

 // Example 3 - Open the default email application.
 vscode.env.openExternal(vscode.Uri.parse('mailto:'));
 }));
}
import * as vscode from 'vscode';
import { getExpressServerPort } from './server';

export async function activate(context: vscode.ExtensionContext) {

 const dynamicServerPort = await getWebServerPort();

 context.subscriptions.push(vscode.commands.registerCommand('myAmazingExtension.forwardLocalhost', async () =>

 // Make the port available locally and get the full URI
 const fullUri = await vscode.env.asExternalUri(
 vscode.Uri.parse(`http://localhost:${dynamicServerPort}`));

 // ... do something with the fullUri ...

 }));
}
import * as vscode from 'vscode';

// This is ${publisher}.${name} from package.json
const extensionId = 'my.amazing-extension';

export async function activate(context: vscode.ExtensionContext) {

 // Register a URI handler for the authentication callback
 vscode.window.registerUriHandler({
 handleUri(uri: vscode.Uri): vscode.ProviderResult {

 // Add your code for what to do when the authentication completes here.
 if (uri.path === '/auth-complete') {
 vscode.window.showInformationMessage('Sign in successful!');
 }

 }
 });

 // Register a sign in command
 context.subscriptions.push(vscode.commands.registerCommand(`${extensionId}.signin`, async () => {

 // Get an externally addressable callback URI for the handler that the authentication provider can use
 const callbackUri = await vscode.env.asExternalUri(vscode.Uri.parse(`${vscode.env.uriScheme}://${extensionId}/auth-complete`));

 // Add your code to integrate with an authentication provider here - we'll fake it.
 vscode.env.clipboard.writeText(callbackUri.toString());
 await vscode.window.showInformationMessage('Open the URI copied to the clipboard in a browser window to authorize.');
 }));
}
import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {

 // extensionKind returns ExtensionKind.UI when running locally, so use this to detect remote
 const extension = vscode.extensions.getExtension('your.extensionId');
 if (extension.extensionKind === vscode.ExtensionKind.Workspace) {
 vscode.window.showInformationMessage('I am running remotely!');
 }

 // Codespaces browser-based editor will return UIKind.Web for uiKind
 if (vscode.env.uiKind === vscode.UIKind.Web) {
 vscode.window.showInformationMessage('I am running in the Codespaces browser editor!');
 }

 // VS Code will return undefined for remoteName if working with a local workspace
 if (typeof(vscode.env.remoteName) === 'undefined') {
 vscode.window.showInformationMessage('Not currently connected to a remote workspace.');
 }

}
import * as vscode from 'vscode';

export async function activate(context: vscode.ExtensionContext) {
 // Register the private echo command
 const echoCommand = vscode.commands.registerCommand('_private.command.called.echo',
 (value: string) => {
 return value;
 }
 );
 context.subscriptions.push(echoCommand);
}
// Create the webview
const panel = vscode.window.createWebviewPanel(
 'catWebview',
 'Cat Webview',
 vscode.ViewColumn.One);

// Get the content Uri
const catGifUri = panel.webview.asWebviewUri(
 vscode.Uri.joinPath(context.extensionUri, 'media', 'cat.gif'));

// Reference it in your content
panel.webview.html = `

 

`;
// Use asExternalUri to get the URI for the web server
const dynamicWebServerPort = await getWebServerPort();
const fullWebServerUri = await vscode.env.asExternalUri(
 vscode.Uri.parse(`http://localhost:${dynamicWebServerPort}`)
 );

// Create the webview
const panel = vscode.window.createWebviewPanel(
 'asExternalUriWebview',
 'asExternalUri Example',
 vscode.ViewColumn.One, {
 enableScripts: true
 });

const cspSource = panel.webview.cspSource;
panel.webview.html = `
 
 
 
 
 
 
 
 `;
const LOCAL_STATIC_PORT = 3000;
const dynamicServerPort = await getWebServerPort();

// Create webview and pass portMapping in
const panel = vscode.window.createWebviewPanel(
 'remoteMappingExample',
 'Remote Mapping Example',
 vscode.ViewColumn.One, {
 portMapping: [
 // This maps localhost:3000 in the webview to the web server port on the remote host.
 { webviewPort: LOCAL_STATIC_PORT, extensionHostPort: dynamicServerPort }
 ]
 });

// Reference the port in any full URIs you reference in your HTML.
panel.webview.html = `
 
 
 
 
 `;
function requireWithFallback(electronModule: string, nodeModule: string) {
 try {
 return require(electronModule);
 }
 catch (err) { }
 return require(nodeModule);
}

const fs = requireWithFallback('original-fs', 'fs');
npm install --save-dev eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin
yarn add eslint @typescript-eslint/parser @typescript-eslint/eslint-plugin --dev
npx tslint-to-eslint-config
"lint": "eslint -c .eslintrc.js --ext .ts "
"recommendations": [
 "dbaeumer.vscode-eslint"
 ]
> npx @vscode/dts dev
Downloading vscode.proposed.languageStatus.d.ts
To: /Users/Me/Code/MyExtension/vscode.proposed.languageStatus.d.ts
From: https://raw.githubusercontent.com/microsoft/vscode/main/src/vscode-dts/vscode.proposed.languageStatus.d.ts
Read more about proposed API at: https://code.visualstudio.com/api/advanced-topics/using-proposed-api
{
 ...
 "enable-proposed-api": [""]
}
// on activate
const versionKey = 'shown.version';
context.globalState.setKeysForSync([versionKey]);

// later on show page
const currentVersion = context.extension.packageJSON.version;
const lastVersionShown = context.globalState.get(versionKey);
if (isHigher(currentVersion, lastVersionShown)) {
 context.globalState.update(versionKey, currentVersion);
}
npx --package yo --package generator-code -- yo code
# ? What type of extension do you want to create? New Extension (TypeScript)
# ? What's the name of your extension? Code Tutor

### Press to choose default for all options below ###

# ? What's the identifier of your extension? code-tutor
# ? What's the description of your extension? LEAVE BLANK
# ? Initialize a git repository? Yes
# ? Bundle the source code with webpack? No
# ? Which package manager to use? npm

# ? Do you want to open the new folder with Visual Studio Code? Open with `code`
"contributes":{
 "chatParticipants": [
 {
 "id": "chat-tutorial.code-tutor",
 "fullName": "Code Tutor",
 "name": "tutor",
 "description": "What can I teach you?",
 "isSticky": true
 }
 ]
}
const BASE_PROMPT = 'You are a helpful code tutor. Your job is to teach the user with simple descriptions and sample code of the concept. Respond with a guided overview of the concept in a series of messages. Do not give the user the answer directly, but guide them to find the answer themselves. If the user asks a non-programming question, politely decline to respond.';
// define a chat handler
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

 return;
}
// define a chat handler
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

 // initialize the prompt
 let prompt = BASE_PROMPT;

 // initialize the messages array with the prompt
 const messages = [
 vscode.LanguageModelChatMessage.User(prompt),
 ];

 // add in the user's message
 messages.push(vscode.LanguageModelChatMessage.User(request.prompt));

 // send the request
 const chatResponse = await request.model.sendRequest(messages, {}, token);

 // stream the response
 for await (const fragment of chatResponse.text) {
 stream.markdown(fragment);
 }

 return;
};
// define a chat handler
const handler: vscode.ChatRequestHandler = async (request: vscode.ChatRequest, context: vscode.ChatContext, stream: vscode.ChatResponseStream, token: vscode.CancellationToken) => {

 // initialize the prompt
 let prompt = BASE_PROMPT;

 // initialize the messages array with the prompt
 const messages = [
 vscode.LanguageModelChatMessage.User(prompt),
 ];

 // add in the user's message
 messages.push(vscode.LanguageModelChatMessage.User(request.prompt));

 // send the request
 const chatResponse = await request.model.sendRequest(messages, {}, token);
```

## Source 2: C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\ask-agent\Ask.agent.md

- Characters: 2376

```text
---
name: Ask
description: Answers questions without making changes
argument-hint: Ask a question about your code or project
target: vscode
disable-model-invocation: true
tools: ['search', 'read', 'web', 'vscode/memory', 'github/issue_read', 'github.vscode-pull-request-github/issue_fetch', 'github.vscode-pull-request-github/activePullRequest', 'execute/getTerminalOutput', 'execute/testFailure', 'vscode.mermaid-chat-features/renderMermaidDiagram', 'vscode/askQuestions']
agents: []
---
You are an ASK AGENT — a knowledgeable assistant that answers questions, explains code, and provides information.

Your job: understand the user's question → research the codebase as needed → provide a clear, thorough answer. You are strictly read-only: NEVER modify files or run commands that change state.

<rules>
- NEVER use file editing tools, terminal commands that modify state, or any write operations
- Focus on answering questions, explaining concepts, and providing information
- Use search and read tools to gather context from the codebase when needed
- Provide code examples in your responses when helpful, but do NOT apply them
- Use #tool:vscode/askQuestions to clarify ambiguous questions before researching
- When the user's question is about code, reference specific files and symbols
- If a question would require making changes, explain what changes would be needed but do NOT make them
</rules>

<capabilities>
You can help with:
- **Code explanation**: How does this code work? What does this function do?
- **Architecture questions**: How is the project structured? How do components interact?
- **Debugging guidance**: Why might this error occur? What could cause this behavior?
- **Best practices**: What's the recommended approach for X? How should I structure Y?
- **API and library questions**: How do I use this API? What does this method expect?
- **Codebase navigation**: Where is X defined? Where is Y used?
- **General programming**: Language features, algorithms, design patterns, etc.
</capabilities>

<workflow>
1. **Understand** the question — identify what the user needs to know
2. **Research** the codebase if needed — use search and read tools to find relevant code
3. **Clarify** if the question is ambiguous — use #tool:vscode/askQuestions
4. **Answer** clearly — provide a well-structured response with references to relevant code
</workflow>
```

## Source 3: C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\copilotCli\copilotcli.session.metadata.json

- Characters: 12000

```text
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\AGENTS_INDEX.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\AGENTS_INDEX.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\BACKEND_DEPLOYMENT_FINAL.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\BACKEND_DEPLOYMENT_FINAL.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\CONSTRAINTS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\CONSTRAINTS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\CONSTRAINT_BREAKDOWN.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\CONSTRAINT_BREAKDOWN.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\DEPLOYMENT_STATUS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\DEPLOYMENT_STATUS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\DEPLOYMENT_SUCCESS_020226.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\DEPLOYMENT_SUCCESS_020226.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\ENVIRONMENT_SETUP.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\ENVIRONMENT_SETUP.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\EXECUTION_SUMMARY.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\EXECUTION_SUMMARY.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\INDEX.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\INDEX.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\LINK_STATUS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\LINK_STATUS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\PROGRESS_REPORT_FINAL.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\PROGRESS_REPORT_FINAL.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\QUICK_START_GUIDE.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\QUICK_START_GUIDE.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\README.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\README.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\SPRINT_COMPLETION_REPORT.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\SPRINT_COMPLETION_REPORT.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\STATUS_FINAL_020226.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\STATUS_FINAL_020226.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\SUMMARY_CONSTRAINT_CLARIFICATION.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\SUMMARY_CONSTRAINT_CLARIFICATION.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\01_schema.sql
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\01_schema.sql
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\01_schema_clean.sql
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\01_schema_clean.sql
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\execute_schema.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\execute_schema.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\queries.sql
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\queries.sql
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\run.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\run.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\validate_schema.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-1-data-engineer\validate_schema.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-2-backend-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-2-backend-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-2-backend-engineer\BACKEND_REVIEW.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-2-backend-engineer\BACKEND_REVIEW.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-3-frontend-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-3-frontend-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-4-payments-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\agent-4-payments-engineer\AGENT_INSTRUCTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\test_backend.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.agents\test_backend.py
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.github\copilot-instructions.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.github\copilot-instructions.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.github\copilot-instructions.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.vscode\settings.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.vscode\settings.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.vscode\settings.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.vscode\tasks.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.vscode\tasks.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\.vscode\tasks.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\AzuriteConfig
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\AzuriteConfig
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_blob__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_blob__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_blob_extent__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_blob_extent__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_queue__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_queue__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_queue_extent__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_queue_extent__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_table__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\__azurite_db_table__.json
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\deploy-backend.ps1
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\deploy-backend.ps1
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\CHECKPOINT_31_01_2026.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\CHECKPOINT_31_01_2026.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\FLUXO_MVP_REAL.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\FLUXO_MVP_REAL.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\FLUXO_REAL_TOPOGRAFO_CLIENTE.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\FLUXO_REAL_TOPOGRAFO_CLIENTE.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\FREE_AI_OPTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\FREE_AI_OPTIONS.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\ISOLAMENTO_INFINITEPAY_31_01.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\ISOLAMENTO_INFINITEPAY_31_01.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\JAMBA_INTEGRATION.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\JAMBA_INTEGRATION.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\MVP_PLANO_EXECUCAO.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\MVP_PLANO_EXECUCAO.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\OPENROUTER_INTEGRATION.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\OPENROUTER_INTEGRATION.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\OPENROUTER_QUICKSTART.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\OPENROUTER_QUICKSTART.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\PROPOSTA_ARQUITETURA_SINGLE_PAGE_LOGIN.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\PROPOSTA_ARQUITETURA_SINGLE_PAGE_LOGIN.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\QUICK_START_OPENROUTER.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\QUICK_START_OPENROUTER.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\REFACTORING_PLAN.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\REFACTORING_PLAN.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\REQUIREMENTS_CONSOLIDADO.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree-2026-02-01T04-52-11\novo-projeto\REQUIREMENTS_CONSOLIDADO.md
c:\Users\User\cooking-agent\ai1.worktrees\copilot-worktree
```

## Source 4: C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\explore-agent\Explore.agent.md

- Characters: 2062

```text
---
name: Explore
description: Fast read-only codebase exploration and Q&A subagent. Prefer over manually chaining multiple search and file-reading operations to avoid cluttering the main conversation. Safe to call in parallel. Specify thoroughness: quick, medium, or thorough.
argument-hint: Describe WHAT you're looking for and desired thoroughness (quick/medium/thorough)
model: ['Claude Haiku 4.5 (copilot)', 'Gemini 3 Flash (Preview) (copilot)', 'Auto (copilot)']
target: vscode
user-invocable: false
tools: ['search', 'read', 'web', 'vscode/memory', 'github/issue_read', 'github.vscode-pull-request-github/issue_fetch', 'github.vscode-pull-request-github/activePullRequest', 'execute/getTerminalOutput', 'execute/testFailure']
agents: []
---
You are an exploration agent specialized in rapid codebase analysis and answering questions efficiently.

## Search Strategy

- Go **broad to narrow**:
 1. Start with glob patterns or semantic codesearch to discover relevant areas
 2. Narrow with text search (regex) or usages (LSP) for specific symbols or patterns
 3. Read files only when you know the path or need full context
- Pay attention to provided agent instructions/rules/skills as they apply to areas of the codebase to better understand architecture and best practices.
- Use the github repo tool to search references in external dependencies.

## Speed Principles

Adapt search strategy based on the requested thoroughness level.

**Bias for speed** — return findings as quickly as possible:
- Parallelize independent tool calls (multiple greps, multiple reads)
- Stop searching once you have sufficient context
- Make targeted searches, not exhaustive sweeps

## Output

Report findings directly as a message. Include:
- Files with absolute links
- Specific functions, types, or patterns that can be reused
- Analogous existing features that serve as implementation templates
- Clear answers to what was asked, not comprehensive overviews

Remember: Your goal is searching efficiently through MAXIMUM PARALLELISM to report concise and clear answers.
```

## Source 5: C:\Users\User\AppData\Roaming\Code\User\globalStorage\github.copilot-chat\plan-agent\Plan.agent.md

- Characters: 5190

```text
---
name: Plan
description: Researches and outlines multi-step plans
argument-hint: Outline the goal or problem to research
target: vscode
disable-model-invocation: true
tools: ['search', 'read', 'web', 'vscode/memory', 'github/issue_read', 'github.vscode-pull-request-github/issue_fetch', 'github.vscode-pull-request-github/activePullRequest', 'execute/getTerminalOutput', 'execute/testFailure', 'agent', 'vscode/askQuestions']
agents: ['Explore']
handoffs:
 - label: Start Implementation
 agent: agent
 prompt: 'Start implementation'
 send: true
 - label: Open in Editor
 agent: agent
 prompt: '#createFile the plan as is into an untitled file (`untitled:plan-${camelCaseName}.prompt.md` without frontmatter) for further refinement.'
 send: true
 showContinueOn: false
---
You are a PLANNING AGENT, pairing with the user to create a detailed, actionable plan.

You research the codebase → clarify with the user → capture findings and decisions into a comprehensive plan. This iterative approach catches edge cases and non-obvious requirements BEFORE implementation begins.

Your SOLE responsibility is planning. NEVER start implementation.

**Current plan**: `/memories/session/plan.md` - update using #tool:vscode/memory.

<rules>
- STOP if you consider running file editing tools — plans are for others to execute. The only write tool you have is #tool:vscode/memory for persisting plans.
- Use #tool:vscode/askQuestions freely to clarify requirements — don't make large assumptions
- Present a well-researched plan with loose ends tied BEFORE implementation
</rules>

<workflow>
Cycle through these phases based on user input. This is iterative, not linear. If the user task is highly ambiguous, do only *Discovery* to outline a draft plan, then move on to alignment before fleshing out the full plan.

## 1. Discovery

Run the *Explore* subagent to gather context, analogous existing features to use as implementation templates, and potential blockers or ambiguities. When the task spans multiple independent areas (e.g., frontend + backend, different features, separate repos), launch **2-3 *Explore* subagents in parallel** — one per area — to speed up discovery.

Update the plan with your findings.

## 2. Alignment

If research reveals major ambiguities or if you need to validate assumptions:
- Use #tool:vscode/askQuestions to clarify intent with the user.
- Surface discovered technical constraints or alternative approaches
- If answers significantly change the scope, loop back to **Discovery**

## 3. Design

Once context is clear, draft a comprehensive implementation plan.

The plan should reflect:
- Structured concise enough to be scannable and detailed enough for effective execution
- Step-by-step implementation with explicit dependencies — mark which steps can run in parallel vs. which block on prior steps
- For plans with many steps, group into named phases that are each independently verifiable
- Verification steps for validating the implementation, both automated and manual
- Critical architecture to reuse or use as reference — reference specific functions, types, or patterns, not just file names
- Critical files to be modified (with full paths)
- Explicit scope boundaries — what's included and what's deliberately excluded
- Reference decisions from the discussion
- Leave no ambiguity

Save the comprehensive plan document to `/memories/session/plan.md` via #tool:vscode/memory, then show the scannable plan to the user for review. You MUST show plan to the user, as the plan file is for persistence only, not a substitute for showing it to the user.

## 4. Refinement

On user input after showing the plan:
- Changes requested → revise and present updated plan. Update `/memories/session/plan.md` to keep the documented plan in sync
- Questions asked → clarify, or use #tool:vscode/askQuestions for follow-ups
- Alternatives wanted → loop back to **Discovery** with new subagent
- Approval given → acknowledge, the user can now use handoff buttons

Keep iterating until explicit approval or handoff.
</workflow>

<plan_style_guide>
```markdown
## Plan: {Title (2-10 words)}

{TL;DR - what, why, and how (your recommended approach).}

**Steps**
1. {Implementation step-by-step — note dependency ("*depends on N*") or parallelism ("*parallel with step N*") when applicable}
2. {For plans with 5+ steps, group steps into named phases with enough detail to be independently actionable}

**Relevant files**
- `{full/path/to/file}` — {what to modify or reuse, referencing specific functions/patterns}

**Verification**
1. {Verification steps for validating the implementation (**Specific** tasks, tests, commands, MCP tools, etc; not generic statements)}

**Decisions** (if applicable)
- {Decision, assumptions, and includes/excluded scope}

**Further Considerations** (if applicable, 1-3 items)
1. {Clarifying question with recommendation. Option A / Option B / Option C}
2. {…}
```

Rules:
- NO code blocks — describe changes, link to files and specific symbols/functions
- NO blocking questions at the end — ask during workflow via #tool:vscode/askQuestions
- The plan MUST be presented to the user, don't just mention the plan file.
</plan_style_guide>
```

## Source 6: C:\Users\User\AppData\Roaming\Code\User\workspaceStorage\0010d70cd6e65ecb79a3ac5e6b167e45\workspace.json

- Characters: 82

```text
file:///c%3A/Users/User/aqkin/aqkin.worktrees/copilot-worktree-2026-02-03T03-18-17
```
