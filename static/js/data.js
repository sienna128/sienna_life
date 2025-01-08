document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_data')
        .then(response => response.json)
        .then(json => {
            data = json;
        })
        .catch(err => console.error("Error fetching data: ", err));
});

function showContent() {
    const option = document.getElementById('model-select').value;

    if (option) {
        const contentDiv = document.getElementById('model-content');
        console.log("HERE", option, contentDiv)
        console.log("data try", data);
        console.log("todos try", data["todos"]);
        contentDiv.innerHTML = data[option];
    }
}