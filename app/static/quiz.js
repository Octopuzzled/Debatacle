// Get the search input and button elements
const searchInput = document.querySelector('.form-control[type="search"]');
const searchButton = document.querySelector('.btn[type="submit"]');

// Add an event listener to the search button
searchButton.addEventListener('click', (event) => {
  event.preventDefault(); // Prevent the default form submission
  performSearch();
});

// Add an event listener to the search input for 'keyup' events
searchInput.addEventListener('keyup', (event) => {
  if (event.key === 'Enter') {
    performSearch();
  }
});

function performSearch() {
  // Get the search query from the input
  const searchQuery = searchInput.value.toLowerCase().trim();

  // Filter your data (e.g., an array of objects) based on the search query
  // This is where you'll need to implement your own logic to search your data
  const filteredData = data.filter((item) =>
    item.title.toLowerCase().includes(searchQuery)
  );

  // Update the UI to display the filtered results
  updateSearchResults(filteredData);
}

function updateSearchResults(results) {
  // This is where you'll need to implement the logic to update your UI
  // with the search results. For example, you could populate a list or table
  // with the filtered data.
  console.log(results);
}