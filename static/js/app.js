const BASE_URL = "http://127.0.0.1:5000/";


$('.saveDrink').on('click', async function (e) {
    let id = $(this).data('id')
    let resp = await axios.post(`${BASE_URL}drinks/save/${id}`)
    if (resp.data.message == 'Saved') {
        let cls = $(this).attr('class', 'btn btn-danger').text('Remove Save')
    } else if (resp.data.message == 'Removed') {
        let cls = $(this).attr('class', 'btn btn-success').text('Save to Favorites')
    }
})


$('.saveIngredient').on('click', async function (e) {
    let id = $(this).data('id')
    let resp = await axios.post(`${BASE_URL}ingredients/save/${id}`)
    if (resp.data.message == 'Saved') {
        let cls = $(this).attr('class', 'btn btn-danger').text('Remove Save')
    } else if (resp.data.message == 'Removed') {
        let cls = $(this).attr('class', 'btn btn-success').text('Save to Favorites')
    }
})

$('.deleteOg').on('click', async function (e) {
    if (confirm("Are you sure you want to delete this recipe?")) {
        let id = $(this).data('id')
        let resp = await axios.post(`${BASE_URL}users/original/delete/${id}`)
        let card = $(this).closest('.parentCard').remove()
    } else {
        return
    }
})
