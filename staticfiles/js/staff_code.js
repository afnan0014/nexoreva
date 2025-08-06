document.addEventListener("DOMContentLoaded", function () {
  console.log("✅ staff_code.js loaded"); // <--- Debug log here

  const roleField = document.getElementById("id_role");
  const codeField = document.getElementById("id_staff_code");

  function generateCode(role) {
    const prefix = role === "Intern" ? "nxrint" : "nxremp";
    const randomNum = Math.floor(1000 + Math.random() * 9000);
    return `${prefix}${randomNum}`;
  }

  if (roleField && codeField) {
    // On role change, always update code
    roleField.addEventListener("change", function () {
      if (roleField.value === "Intern" || roleField.value === "Employee") {
        codeField.value = generateCode(roleField.value);
      } else {
        codeField.value = "";
      }
    });

    // Optional: set initial code on page load
    if (roleField.value === "Intern" || roleField.value === "Employee") {
      codeField.value = generateCode(roleField.value);
    }
  }
});
