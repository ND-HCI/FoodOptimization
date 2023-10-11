        // Javascript code is activated inside HTML 
        let items = "{{ data['branded_food_category'] }}";
        items = items.toLowerCase();  // force lowercase on everything
        items = '"' + escapeHTML(items) + '"';  // process and 'decode' the string to a list-like format
        items = items.split(', '); 

        var filteredItems = items;  // in the beginning, set to all items
        // console.log(typeof items, items);

        function filterSearch() {
            // First, clear the list of options in the dropdown 
            document.getElementById("dropdown").innerHTML = "";

            let searchValue = document.getElementById("search").value;
            searchValue = searchValue.toLowerCase();

            // items = ["olives", "cheese", "pizza"]  
            // searchValue = "olive"  // ["olives"]
            filteredItems = items.filter((item) => item.includes(searchValue));  // returns array of filtered items

            // Insert the updated dropdown options into the dropdown (<select> tag)
            for (let item of filteredItems) {
                // Change how the option name looks in the dropdown select display
                // console.log(item);  // 'plant-based milk' becomes Plant-based Milk
                item = item.replaceAll("'", "");
                item = item.replaceAll('"', "");
                item = toTitleCase(item);
                document.getElementById("dropdown").innerHTML += '<option>' + item + '</option>';
            }
        }