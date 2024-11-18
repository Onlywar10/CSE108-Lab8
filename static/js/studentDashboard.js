console.log("Connected with js");

const selectTab = (e, tabID) => {
  // Get the operation of the currently selected tab
  const tab = e.currentTarget.id;
  console.log(tab);

  // If the clicked tab is already selected do nothing
  if (e.currentTarget.className == "classTabActive") {
    return;
  } else {
    // Reset all the tab colors
    document.getElementsByClassName("classTabActive")[0].className = "classTab";

    // Make the currently selected tab colored
    e.currentTarget.className = "classTabActive";

    // Unshow all the tabs
    document.getElementsByClassName("classListInitial")[0].style.display =
      "none";

    var screens = document.getElementsByClassName("classList");
    for (let i = 0; i < screens.length; i++) {
      screens[0].style.display = "none";
    }

    // Make the selected tab the only one showing
    document.getElementById(tabID).style.display = "flex";
  }
};
