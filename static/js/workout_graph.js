document.getElementById('weight-form').addEventListener('submit', function(e) {
    e.preventDefault();

    const formData = new FormData(e.target);

    fetch('/add_weight', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        const graphDiv = document.getElementById('graph');
        Plotly.react(graphDiv, JSON.parse(data.graph).data, JSON.parse(data.graph).layout);
    });
});