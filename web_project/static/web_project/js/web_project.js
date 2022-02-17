function getList() {
    $.ajax({
        url: "/web_project/get-ingredient-list",
        type: "GET",
        dataType: "json",
        success: updateList,
        error: updateError
    });
}

function updateList(ingredients) {

    // Removes items if they not in db
    $("#ingredientList").children().each(function () {
        let my_id = parseInt(this.id.substring("ingredient_".length))
        let id_in_items = false
        $(ingredients).each(function () {
            if (this.id == my_id) id_in_items = true
        })
        if (!id_in_items) this.remove()
    })

    // add if not in list
    $(ingredients).each(function () {
        let ingredientID = "ingredient_" + this.id

        if (document.getElementById(ingredientID) == null) {
            $("#ingredientList").append(
                '<div id="ingredient_' + this.id + '" class="col-sm-2 p-3 text-center">'
                + '<div class="card text-center shadow">'
                + '<img class="card-img" src="../../static/web_project/image/ingredient-bg.png" alt="Card image">'
                + '<div class="card-font card-img-overlay">'
                + '<div class="ingredient_name_display" data-toggle="tooltip" data-placement="left" title="Quantity: ' + this.ingredient_quantity + " " + this.ingredient_unit + '">' + this.ingredient.ingredient_name.toUpperCase() + '</div>'
                + '</div>'
                + '</div>'
                + '<button id="open_modal_"' + this.id + '" class="btn dark-grey btn-sm" type="button" data-toggle="modal" data-target="#edit-modal" data-userIngredient="' + this.id + '">Edit</button>'
                + '</div>'
                + '</div>'
            )
        }

    })
    getTooltip()
}

function getTooltip() {
    $('[data-toggle="tooltip"]').tooltip({
        container: "body"
    });
}

function updateError(xhr) {

    if (xhr.status == 0) {
        displayError("Cannot connect to server")
        return
    }

    if (!xhr.getResponseHeader('content-type') == 'application/json') {
        displayError("Received status=" + xhr.status)
        return
    }

    let response = JSON.parse(xhr.responseText)
    if (response.hasOwnProperty('error')) {
        displayError(response.error)
        return
    }
    displayError(response)
}

function displayError(message) {
    $("#error").append(
        '<div class="alert alert-danger alert-dismissible fade show">' + '<button type="button" class="close" data-dismiss="alert">&times;</button>' + message + '</div>'
    )
}

function cleanError() {
    $(".alert").fadeTo(500, 0).slideUp(500, function () {
        $(this).remove();
    });
}

function addIngredient() {
    // get ingredient id
    let ingredient = $("#ingredients-select").find(":selected").val()
    // get quantity
    let quantity = $('#quantity').val()
    // get unit
    let unit = $('#unit-select').find(":selected").val()

    if (ingredient == "" || unit == "") {
        displayError("Please select an ingredient and a proper unit.")
        return
    }
    if (unit === "no") {
        unit = ""
    }
    if (quantity < 0 || quantity == "") {
        displayError("Please enter a valid number")
        return
    }

    // clear fields
    $("#ingredients-select").val("")
    $("#unit-select").val("")
    $('#quantity').val("")

    $.ajax({
        url: "/web_project/add-ingredient",
        type: "POST",
        data: {
            ingredient_id: ingredient,
            quantity: quantity,
            unit: unit,
            csrfmiddlewaretoken: getCSRFToken(),
        },
        dataType: "json",
        success: updateList,
        error: updateError
    })
}

function updateIngredient(userIngredientID) {
    // get quantity
    let quantity = $('#edit-quantity').val()
    // get unit
    let unit = $('#edit-unit-select').find(":selected").val()

    if (userIngredientID == "" || unit == "") {
        displayError("Please select an ingredient and a proper unit.")
        return
    }
    if (unit === "no") {
        unit = ""
    }
    if (quantity < 0 || quantity == "") {
        displayError("Please enter a valid number")
        return
    }

    // clear fields
    $("#edit-unit-select").val("")
    $('#edit-quantity').val("")

    $.ajax({
        url: "/web_project/update-ingredient",
        type: "POST",
        data: {
            user_ingredient_id: userIngredientID,
            quantity: quantity,
            unit: unit,
            csrfmiddlewaretoken: getCSRFToken(),
        },
        dataType: "json",
        success: updateSingle,
        error: updateError,
    })
}

function updateSingle(ingredient) {
    let ingredientID = "ingredient_" + ingredient.id
    let newTooltip = "Quantity: " + ingredient.ingredient_quantity + " " + ingredient.ingredient_unit
    $('#' + ingredientID).find(".ingredient_name_display").attr('title', newTooltip).tooltip('_fixTitle')
}

function deleteIngredient(userIngredientID) {
    if (userIngredientID == "") {
        displayError("Please select an ingredient and a proper unit.")
        return
    }
    $("#edit-unit-select").val("")
    $('#edit-quantity').val("")

    $.ajax({
        url: "/web_project/delete-ingredient",
        type: "POST",
        data: {
            user_ingredient_id: userIngredientID,
            csrfmiddlewaretoken: getCSRFToken(),
        },
        dataType: "json",
        success: updateList,
        error: updateError,
    })

}

function embedRecipeYoutubeVideo() {
    $(document).ready(() => {
        const recipeVideoDiv = $('#recipe_video_div');
        var requestListUrl = "https://youtube.googleapis.com/youtube/v3/search?part=snippet&maxResults=1&q=" + recipeName + "&type=video&key=AIzaSyCs1qj7koZJODEU2SL0R59znb2btcmwbaw"
        $.get(requestListUrl).then((data) => {
            const videoId = data.items[0].id.videoId;
            console.log(videoId)
            var embedUrl = "https://www.youtube.com/embed/" + videoId + "?feature=oembed"
            recipeVideoDiv.append(
                '<iframe width="200" height="150" src=' + embedUrl + 'frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" allowfullscreen></iframe>'
                + '<hr/>'
            )
        }).catch((e) => {
            recipeVideoDiv.append("Fetech Vidoe Error:" + e.statusText)
        })
    })
}

function hideSpinner() {
    $('#spinner').hide();
} 


function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}

function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
}