document.querySelectorAll('.task-date-con').forEach(function(container) {
    container.addEventListener("click", function() {
        const taskId = container.id.split('-')[3];
        const dateId = container.id.split('-')[4];

        const checkbox = document.getElementById("checkbox-img-" + taskId+ "-" + dateId);

        const isChecked = checkbox.src.includes("teal_checkmark.png");

        if (isChecked) {
            checkbox.src = "/static/images/teal_uncheckmark.png";
        } else {
            checkbox.src = "/static/images/teal_checkmark.png";
        }

        // Send the new state to the server using AJAX
        fetch('/update-task-checkbox', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                task_id: taskId,  // Send the todo ID
                date_id: dateId,
                checked: !isChecked  // Send the new state (checked or unchecked)
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("here", data.success)
            if (data.success) {
                const comp_elem = document.querySelector(`#comp-${dateId}`)
                if (comp_elem) {
                    comp_elem.textContent = data.comp
                } else {
                    console.log('comp elem not found for id:', dateId)
                }
                console.log("Task updated:", data);
            }
            
        })
        .catch(error => {
            console.error("Error updating todo:", error);
        });

    });
})

const deleteButtons = document.querySelectorAll(".delete-btn");

deleteButtons.forEach(button => {
    button.addEventListener("click", () => {
        const taskId = button.getAttribute("task-id");
        
        fetch("/delete-task", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ task_id: taskId })
        })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(data.message);
                    location.reload(); //refresh the page
                } else {
                    alert(data.message);
                }
            })
            .catch(error => console.error("Error!: ", error));
    })
})