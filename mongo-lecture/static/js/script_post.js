 window.onload = function () {
 console.log("loaded script_post.js");
 document
    .querySelector("#insertPlantFormFetchPost")
    .addEventListener("submit", async function (event) {
      event.preventDefault();

      console.log("post form clicked")
       let form = document.querySelector("#insertPlantFormFetchPost");
      let data = new FormData(form);
       try {
        let res = await fetch("/postPlantFormFetch",
            {
                method: 'POST',
                body:data

            }
        );
        let resJSON = await res.json();
        console.log(resJSON);
        document.querySelector("#results").innerHTML = `<img src = ${resJSON.imagePath}>`
      } catch (err) {
        console.log(err);
      }
})
};