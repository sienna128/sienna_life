const eventsContainer = document.querySelectorAll(".date-info")
let isMouseDown = false;
let startSlot = null;
let activeEvent = null;

const modal = document.getElementById("event-modal");
const closeButton = document.querySelector(".close-button");



eventsContainer.forEach((dateSlots) => {

    dateSlots.setAttribute("draggable", "false");

    dateSlots.addEventListener("mousedown", (e) => {
        isMouseDown = true;

        const slot = e.target;
        //console.log("mouse down", e.target)
        if (slot.classList.contains("date-slot")) {
            startSlot = slot;
            startSlot.style.backgroundColor = "teal";
        }
    })

    dateSlots.addEventListener("mousemove", (e) => {
        //console.log("mousemove", e.target)
        if (isMouseDown && startSlot != null) {
            
            const currentSlot = e.target;
            //console.log("inside", currentSlot)
            if (currentSlot.classList.contains("date-slot")) {
                //console.log("in inside", currentSlot)
                currentSlot.style.backgroundColor = "teal";
            }
        }
    })

    dateSlots.addEventListener("mouseup", (e) => {
        if (isMouseDown) {
            isMouseDown = false;
            slot = e.target;

            start = startSlot.dataset.time;
            end = slot.dataset.timeend;
            date = startSlot.dataset.date;
            
            openModal(start, end, date);

            const eventData = {
                start: startSlot.dataset.time, 
                end: slot.dataset.time,
                date: startSlot.dataset.date
            };

            fetch("/save_event", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(eventData)
            })
                .then(response => response.json())
                .then(data => {
                    console.log("Event saved: ", data);
                })
                .catch(err => console.error("Error saving event: ", err));
        }
    });
});

document.addEventListener("mouseup", (e) => {
    isMouseDown = false;
});

document.addEventListener("dragstart", (e) => {
    e.preventDefault();
});

closeButton.addEventListener("click", () => {
    modal.style.display = "none";
})

function openModal(start, end, date) {
    modal.style.display = 'block';

    console.log(start, end);
    console.log(typeof(start));
    document.getElementById('event-start').value = start;
    document.getElementById('event-end').value = end; 
    document.getElementById('event-date').value = date;
}