const eventsContainer = document.querySelectorAll(".date-info")
let isMouseDown = false;
let startSlot = null;
let activeEvent = null;

let slotsList = [];
let lastSlot = null;

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
            lastSlot = slot;
            console.log("down start", startSlot);
            startSlot.style.backgroundColor = "teal";
            slotsList.push(slot);
        }
    })

    dateSlots.addEventListener("mousemove", (e) => {
        //console.log("mousemove", e.target)
        if (isMouseDown && startSlot != null) {
            
            const currentSlot = e.target;
            //console.log("inside", currentSlot)
            console.log(currentSlot);
            console.log(currentSlot in slotsList, currentSlot == lastSlot, slotsList.length);
            console.log(slotsList.indexOf(currentSlot));
            if (currentSlot.classList.contains("date-slot")) {
                
                if (slotsList.indexOf(currentSlot) > -1) {
                //console.log("in inside", currentSlot)
                    currentSlot.style.backgroundColor = "teal";
                    lastSlot = currentSlot;
                    slotsList.push(currentSlot);
                } else {
                    if (currentSlot != lastSlot) {
                        currentSlot.style.backgroundColor = "aquamarine";
                        slotsList.splice(slotsList.indexOf(currentSlot), 1);
                    }
                }
            }
        }
    })

    dateSlots.addEventListener("mouseup", (e) => {
        if (isMouseDown) {
            isMouseDown = false;
            slot = e.target;

            console.log("up start", startSlot);
            console.log("up end slot", slot);
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

    console.log("open modal", start, end);
    console.log("start type", typeof(start));
    document.getElementById('event-start').value = start;
    document.getElementById('event-end').value = end; 
    document.getElementById('event-date').value = date;
}

fetch('/get_events')
    .then(response => response.json())
    .then(events => {
        const eventsContainer = document.querySelector('.events');

        events.forEach(event => {
            const eventString = event.start_time + "-" + event.date
            console.log("Event String: ", eventString);
            const eventElement = document.getElementById(eventString);
            if (eventElement) {
                eventElement.style.height = `${event.time_slots * 5}%`;
                console.log("make event height: ", event.time_slots*5);
                eventElement.style.backgroundColor = event.color;
            } else {
                console.error("Event element not found: ", event, eventString);
            }
        });
    })
    