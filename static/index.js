function deleteStaff(id) {

    fetch("/delete_staff", {
        method: "POST",
        body: JSON.stringify({ id: id })
    }).then((_res) => {
        window.location.href = "/roster";
    });
}

function updateStaff(id, name, contract, cando1, cando2) {

    fetch("/update_staff", {
        method: "POST",
        body: JSON.stringify({
            id: id, name: name, contract: contract, cando1: cando1, cando2: cando2 })
    }).then((_res) => {
        window.location.href = "/roster";
    });
}