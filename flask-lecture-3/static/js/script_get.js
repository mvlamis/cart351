window.onload = function () {
    console.log("loaded script_get.js");
    document.querySelector("#insertPlantFormFetch").addEventListener("submit", async function (event) {
        event.preventDefault();
        console.log("button clicked");
        const htmlForm = document.querySelector("#insertPlantFormFetch");
        const formData = new FormData(htmlForm);
        const queryParams = new URLSearchParams(formData).toString();
        const url = `/getDataFromForm?${queryParams}`;

        try {
            let res = await fetch(url)
            let resJSON = await res.json()
            console.log(resJSON)

            document.querySelector("#results").innerHTML +=
                `<p> THE NEW RESULT: <mark style = "background:orange">${resJSON.data_received}</mark></p>
       <p> THANK YOU : <mark style = "background:orange">${resJSON.owner}</mark></p>`

        }
        catch (err) {
            console.log(err)
        }

    })
}