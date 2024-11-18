console.log("add course js file connected");

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
