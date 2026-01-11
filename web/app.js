function goToForm() {
  document.getElementById("welcome").classList.remove("active");
  document.getElementById("form").classList.add("active");
}

function showInstruction() {
  const instr = document.getElementById("instruction");
  instr.classList.add("active");
}
