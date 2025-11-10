window.onload = function (){
        console.log("ready");
        document.querySelector("#searchForm").addEventListener("submit", function(){
            event.preventDefault();
            console.log("button clicked");
            console.log("form has been submitted");
            let formData = new FormData(document.querySelector("#searchForm"));
            formData.append("submitSearch","extraTest");
            /* excellent function */
            const queryString = new URLSearchParams(formData).toString();

            fetch("passToFlask?"+queryString)
           .then(function (response) {
            return response.json();
          })
          .then(function (jsonData) {
          console.log(jsonData);
          displayResponse(jsonData["test-response"])
        });

        })
    }

     function displayResponse(theResult) {
    document.querySelector("#result").innerHTML = "";
    let back = document.createElement("div");
    back.id = "back";
    let title = document.createElement("h3");
    title.textContent = "Results from user";
    document.querySelector("#result").appendChild(title);
    document.querySelector("#result").appendChild(back);

    for (let i = 0; i < theResult.length; i++) {
      let container = document.createElement("div");
      container.classList.add("outer");
      back.appendChild(container);

      let contentContainer = document.createElement("div");
      contentContainer.classList.add("content");
      container.appendChild(contentContainer);

      for (let property in theResult[i]) {
        console.log(property);

        if (property !== "imagePath" && property !== "birthDate") {
          let para = document.createElement("p");
          para.textContent = property + ":" + theResult[i][property];
          contentContainer.appendChild(para);
        }
        if(property ==="birthDate"){
          let para = document.createElement("p");
          let options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
          let date = new Date(theResult[i][property]["$date"])
          para.textContent = property + ":" + date.toLocaleDateString("en-US", options);
         contentContainer.appendChild(para);
        }
      }
      let img = document.createElement("img");
      img.setAttribute("src", "../static/"+theResult[i]["imagePath"]);
      container.appendChild(img);
    } //outer for
  }