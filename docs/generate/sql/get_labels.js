// run on https://github.com/snake-biscuits/bsp_tool/labels
// might need to run on multiple pages & comment out 1st line (const redeclaration error)
const issues = document.getElementsByClassName("IssueLabel");
var out = "";
for (const issue of issues) {
  if (issue.children.length == 1) {
    var name = issue.children[0].outerText;
    if (name.includes(".") && !name.startsWith("extensions")) {
      var hex = "";
      issue.getAttribute("style").split(";", 3).forEach((s) => hex += Number(s.substring(10)).toString(16).padStart(2, "0"));
      out += `"${name}": "${hex.toUpperCase()}",\n`;
    }
  }
}
console.log(out);
