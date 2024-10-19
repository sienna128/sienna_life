console.log("Workout.js: start");

const ex_btn = document.getElementById("new-exercise-btn");
const ex_input = document.getElementById("new-exercise-input");
const frm = document.getElementsByName('new-exercise-form')[0];
const frm_ex = document.getElementsByName('exercise-content-form')[0];


frm.addEventListener("submit", function(e) {
    console.log("Workout.js: submit ");
    e.preventDefault();
    frm.submit();
    frm.reset();
});


frm_ex.addEventListener("submit", function(e) {
    console.log("Workout.js: submit ex")
    e.preventDefault();
    frm_ex.submit();
})

$('workout-submit-btn-container').hide()