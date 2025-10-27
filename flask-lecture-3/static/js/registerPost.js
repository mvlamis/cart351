window.onload = function () {
    console.log("loaded post script");
    document
        .querySelector("#insertRegForm")
        .addEventListener("submit", async function (event) {
            event.preventDefault();
            console.log("button clicked");

            let form = document.querySelector("#insertRegForm");
            let data = new FormData(form);

            try {
                let res = await fetch("/postRegFormFetch",
                    {
                        method: 'POST',
                        body: data

                    }
                );
                let resJSON = await res.json();
                console.log(resJSON);
                document.querySelector("#reg_thank").innerHTML =
                    `<h3> Thank you 
            <span class = "highlight">${resJSON.f_name}</span> for registering !</h3>`;
            } catch (err) {
                console.log(err);
            }

        });
};