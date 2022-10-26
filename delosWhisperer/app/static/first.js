function downloadCourseByRid(rid, name) {
    alert("Requesting download of course: " + name)
    const options = {
        method: 'GET',
        mode: 'cors',
        cache: 'default',
    };
    const params = new URLSearchParams({
        rid: rid,
        name: name
    }).toString()
    const myRequest = new Request("http://127.0.0.1:8000/app/downloadCourse?" + params);
    fetch(myRequest, options)
        .then((response) => {
            console.log(response)
            return response.json();
        })
        .then(responseBody => {
            alert(responseBody);
        });
}
