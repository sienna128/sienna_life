const eventsContainer = document.querySelectorAll(".date-info")
let isMouseDown = false;
let startSlot = null;
let activeEvent = null;

let slotsList = [];
let lastSlot = null;

let startDefault = null;
let endDefault = null;
let dateDefault = null;

const modal = document.getElementById("event-modal");
const closeButton = document.querySelector(".close-button");


//------------ CREATE EVENT HANDLING --------------------------------

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

    dateSlots.addEventListener("mouseover", (e) => {
        //console.log("mouseover", e.target)
        if (isMouseDown && startSlot != null) {
            
            const currentSlot = e.target;
            
            console.log("inside", currentSlot);
            console.log("cS color", currentSlot.style.backgroundColor);
            if (currentSlot.classList.contains("date-slot")) {
                //console.log("in inside", currentSlot)
                if (currentSlot.style.backgroundColor == "teal") {
                    currentSlot.style.backgroundColor = "aquamarine";
                } else {
                    currentSlot.style.backgroundColor = "teal";
                }

                if (lastSlot.dataset.time == currentSlot.dataset.timeend) {
                    lastSlot.style.backgroundColor = "aquamarine";
                }
            }
            lastSlot = currentSlot; 
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
    location.reload();
})

//----------------DROP DOWN HANDLING--------------------------------------------------------

let allSlotsList = [];
let allDatesList = [];

fetch('/get_timeslots')
    .then(response => response.json())
    .then(slots => {
        
        slots.forEach(slot => {
            allSlotsList.push(slot);
            //console.log("slot: ", slot.start);
    
        });
    })
    
fetch('/get_dates')
    .then(response => response.json())
    .then(dates => {
        
        dates.forEach(date => {
            allDatesList.push(date);
            //console.log("date: ", date.date);
    
        });
    })

const dropdownStart = document.getElementById("event-start");
const dropdownEnd = document.getElementById("event-end");
const dropdownDate = document.getElementById("event-date");
   
function openModal(start, end, date) {
    modal.style.display = 'block';

    console.log("open modal", start, end);
    //console.log("start type", typeof(start));


    //document.getElementById('event-start-default').value = start;
    //document.getElementById('event-end-default').value = end; 
    //document.getElementById('event-date-default').value = date;

    startDefault = start;
    endDefault = end;
    dateDefault = date;

    for (let i = 0; i<allSlotsList.length; i++) {
        const option = document.createElement("option");
        option.value = allSlotsList[i].start;
        option.textContent = allSlotsList[i].start;
        if (option.value == startDefault) {
            option.selected = true;
        }
        dropdownStart.appendChild(option);
    }

    for (let i = 0; i<allSlotsList.length; i++) {
        const option = document.createElement("option");
        option.value = allSlotsList[i].start;
        option.textContent = allSlotsList[i].start;
        if (option.value == endDefault) {
            option.selected = true;
        }
        dropdownEnd.appendChild(option);
    }

    for (let i = 0; i<allDatesList.length; i++) {
        const option = document.createElement("option");
        option.value = allDatesList[i].date;
        option.textContent = allDatesList[i].date;
        if (option.value == dateDefault) {
            option.selected = true;
        }
        dropdownDate.appendChild(option);
    }
    
}

dropdownStart.addEventListener("mousedown", () => {
    const selectedIndex = dropdownStart.selectedIndex;
    const itemHeight = dropdownStart.scrollHeight / dropdownStart.options.length;
    console.log("inside start", selectedIndex);
    dropdownStart.scrollTop = itemHeight * (selectedIndex - 4);
})

dropdownEnd.addEventListener("mousedown", () => {
    const selectedIndex = dropdownEnd.selectedIndex;
    const itemHeight = dropdownEnd.scrollHeight / dropdownEnd.options.length;
    console.log("inside end", selectedIndex);
    dropdownEnd.scrollTop = itemHeight * (selectedIndex - 4);
})

dropdownDate.addEventListener("mousedown", () => {
    const selectedIndex = dropdownDate.selectedIndex;
    const itemHeight = dropdownDate.scrollHeight / dropdownDate.options.length;
    console.log("inside date", selectedIndex);
    dropdownDate.scrollTop = itemHeight * (selectedIndex - 4);
})


//--------------- LOAD EVENT DATA --------------------------------------

fetch('/get_events')
    .then(response => response.json())
    .then(events => {
        const eventsContainer = document.querySelector('.events');

        events.forEach(event => {
            const eventString = "event-" + event.id
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

//-------------------- EDITING EVENT HANDLING -------------------------

const events = document.querySelectorAll(".event-con")
console.log("events", events);

events.forEach((event) => {
    event.addEventListener("onclick", (e) => {
        event_obj = e.target;
        console.log("event clicked", event_obj.id, event.id)
    })
});

    