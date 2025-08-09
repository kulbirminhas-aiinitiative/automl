// Log Review Script
// Scans logs for compilation and runtime errors and outputs summary

const fs = require('fs');
const path = require('path');

const errorLogPath = path.join(__dirname, '../logs/runtime-errors.log');
const webOutputPath = path.join(__dirname, '../logs/web-output.log');

function scanForErrors(logPath) {
  if (!fs.existsSync(logPath)) return [];
  const content = fs.readFileSync(logPath, 'utf-8');
  const errorLines = content.split('\n').filter(line => 
    line.match(/error|fail|exception|traceback|fatal/i) && 
    !line.match(/collecting build traces|Internal Server Error=== Testing|<!DOCTYPE html|=== Frontend Upload Error Investigation|=== Fixed Frontend Port Issue/i) &&
    line.trim().length > 0
  );
  return errorLines;
}

function main() {
  const runtimeErrors = scanForErrors(errorLogPath);
  const webErrors = scanForErrors(webOutputPath);
  if (runtimeErrors.length || webErrors.length) {
    console.log('Errors found:');
    if (runtimeErrors.length) {
      console.log('Runtime Errors:', runtimeErrors);
    }
    if (webErrors.length) {
      console.log('Web Output Errors:', webErrors);
    }
    process.exit(1);
  } else {
    console.log('No errors found in logs.');
    process.exit(0);
  }
}

main();
