let data = null;
let divList = [];

document.addEventListener('DOMContentLoaded', () => {
    fetch('/get_data')
        .then(response => response.json())
        .then(json => {
            data = json;
            console.log("fetch", json, data)
        })
        .catch(err => console.error("Error fetching data: ", err));
});

function showContent() {
    const option = document.getElementById('model-select').value;

    for (const div of divList) {
        div.remove();
    }

    divList = []; 

    if (option) {
        const contentDiv = document.getElementById('model-content');
        console.log("HERE", option, contentDiv)
        console.log("data try", JSON.stringify(data));
        console.log("date try", JSON.stringify(data["dates"]));
        console.log("date try 2", data["dates"][0]);
        //contentDiv.innerHTML = JSON.stringify(data[option]);

        for (let i = 0; i < data[option].length; i++) {
            const newDiv = document.createElement('div');
            newDiv.textContent = JSON.stringify(data[option][i]);
            newDiv.style.height = "5%";
            contentDiv.appendChild(newDiv);
            divList.push(newDiv);
        }
    }
}