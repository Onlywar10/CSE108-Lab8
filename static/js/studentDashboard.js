console.log("Connected with js");

const selectTab = (e, tabID) => {
  // Get the operation of the currently selected tab
  const tab = e.currentTarget.id;
  console.log(tab);

  // If the clicked tab is already selected, do nothing
  if (e.currentTarget.className == "classTabActive") {
    return;
  } else {
    // Reset all the tab colors
    document.getElementsByClassName("classTabActive")[0].className = "classTab";

    // Make the currently selected tab colored
    e.currentTarget.className = "classTabActive";

    // Hide all the tabs
    document.getElementsByClassName("classListInitial")[0].style.display =
      "none";

    const screens = document.getElementsByClassName("classList");
    for (let i = 0; i < screens.length; i++) {
      screens[i].style.display = "none";
    }

    // Show the selected tab
    document.getElementById(tabID).style.display = "flex";
  }
};

// Define the classEnroll function
// function classEnroll(buttonElement) {
//   // Parse the button's value (ensure it matches the expected format)
//   const classData = JSON.parse(buttonElement.value);
//   const classId = classData.id;
//   const enrolledStatus = classData.enrolled;

//   // Determine the new status based on the current status
//   const newStatus = enrolledStatus === "+" ? "+" : "-";

//   // Send the enrollment request to the server
//   fetch("/enroll", {
//     method: "POST",
//     headers: {
//       "Content-Type": "application/json",
//     },
//     body: JSON.stringify({
//       id: classId,
//       enrolled: newStatus,
//     }),
//   })
//     .then((response) => {
//       if (!response.ok) {
//         throw new Error("Failed to update enrollment");
//       }
//       return response.text();
//     })
//     .then((message) => {
//       alert(message); // Notify the user
//       location.reload(); // Reload the page to reflect changes
//     })
//     .catch((error) => {
//       console.error("Error enrolling class:", error);
//       alert("Error enrolling class: " + error.message);
//     });
// }

const classEnroll = (buttonElement) => {
  var classData = buttonElement.value;
  classData = classData.replaceAll("'", '"');

  classData = JSON.parse(classData);

  console.log(classData);

  fetch("/enroll", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(classData),
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Failed to enroll in class");
      }
    })
    .catch((error) => {
      console.log(error);
    });

  window.location.reload();
};
