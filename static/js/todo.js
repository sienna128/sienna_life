// Add event listeners to each checkbox container

document.querySelectorAll('.checkbox-con').forEach(function(container) {
    container.addEventListener("click", function() {
        // Get the todo ID
        const todoId = container.id.split('-')[2];
        console.log("todo id", todoId)
        const checkboxImg = document.getElementById("checkbox-img-" + todoId);

        // Get the current state of the checkbox (checked or unchecked)
        const isChecked = checkboxImg.src.includes("teal_checkmark.png");

        // Toggle the checkbox image based on the current state
        if (isChecked) {
            checkboxImg.src = "/static/images/teal_uncheckmark.png";
        } else {
            checkboxImg.src = "/static/images/teal_checkmark.png";
        }

        // Send the new state to the server using AJAX
        fetch('/update-todo-checkbox', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                todo_id: todoId,  // Send the todo ID
                checked: !isChecked  // Send the new state (checked or unchecked)
            })
        })
        .then(response => response.json())
        .then(data => {
            console.log("here", data.success)
            if (data.success) {
                const days_elem = document.querySelector(`#days-l-${todoId}`)
                if (days_elem) {
                    days_elem.textContent = data.days_left;
                    console.log("days elem found")
                } else {
                    console.error("days elem not found for id:", `days-${todoId}`);
                }
                console.log("Todo updated:", data);
            }
            
        })
        .catch(error => {
            console.error("Error updating todo:", error);
        });
    });
});

