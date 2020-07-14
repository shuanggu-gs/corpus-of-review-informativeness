var data;

function create_table(startRow, endRow) {
    var keys = Object.keys(data);
    var values = Object.values(data);
    var num = data[keys[0]].length

    if (document.getElementById("review_table")) {
        document.getElementById("review_table").remove();
    }

    var table = document.createElement('table');
        table.setAttribute('id', 'review_table');

    var header = table.createTHead();
    var hd = header.insertRow();
    for (var j = 0; j < keys.length; j++ ) {
        var cell = hd.insertCell();
         if (j == 0) {
            cell.appendChild(document.createTextNode('#'));
         } else {
            cell.appendChild(document.createTextNode(keys[j]));
         }
    }


    for(var i = startRow; i < endRow; i++ ) {
        var row = table.insertRow();
        for (var j = 0; j < keys.length; j++ ) {
              var cell = row.insertCell();
              cell.appendChild(document.createTextNode(data[keys[j]][i]));
        }
    }
    return table
}

function goPage(pno, psize=20) {

    var keys = Object.keys(data);
    var values = Object.values(data);
    var num = data[keys[0]].length; // number of records

    if (num == 0) {
        alert("Sorry! Nothing Found!")
    } else {
        var totalPage = 0; // number of pages
        var pageSize = psize; // number of records shown on each page

        if (num / pageSize > parseInt(num / pageSize)) {
            totalPage = parseInt(num / pageSize) + 1;
        } else {
            totalPage = parseInt(num / pageSize);
        }

        var currentPage = pno;
        var startRow = (currentPage - 1) * pageSize; // first page start from 0
        var endRow = currentPage * pageSize; // first page end with psize=25
        endRow = (endRow > num) ? num : endRow;


        var maintext = document.getElementById("maintext");
        var table = create_table(startRow, endRow)
        maintext.innerHTML = '';
        maintext.appendChild(table);

        var tempStr = "";
        tempStr += "<button onClick=\"goPage(" + 1 + "," + psize + ")\">First</button>";
        if (currentPage == 1) {
            tempStr += "<button onClick=\"goPage(" + (currentPage) + "," + psize + ")\" disabled>< Prev</button>";
        } else {
            tempStr += "<button onClick=\"goPage(" + (currentPage - 1) + "," + psize + ")\">< Prev</button>";
        }

        tempStr += "<a>" + currentPage + "/" + totalPage + "</a>";
        if (currentPage == totalPage) {
            tempStr += "<button onClick=\"goPage(" + (currentPage) + "," + psize + ")\" disabled>Next ></button>";
        } else {
            tempStr += "<button onClick=\"goPage(" + (currentPage + 1) + "," + psize + ")\">Next ></button>";
        }
        tempStr += "<button onClick=\"goPage(" + totalPage + "," + psize + ")\"> Last</button>";

        document.getElementById("barcon").innerHTML = tempStr;
    }
}

function update_graph(response) {
    var maingraph = document.getElementById("maingraph");
    maingraph.innerHTML = ''
    if (response == 'all') {
        maingraph.innerHTML = "<img src='/imgs/wordcloud.png'>";
    } else {
        maingraph.innerHTML = "<img src='/imgs/"+ response + ".png'>";
    }
}

function enable_level() {
    if (document.getElementById("annotated").checked) {
        document.getElementById("enable_level").style.display = "block";
    }
}

function disable_level() {
    if (document.getElementById("notannotated").checked) {
        document.getElementById("enable_level").style.display = "none";
    }
}

function sumbit_form() {
    var form = document.getElementById("form");
    var formData = new FormData(form);
    var searchParams = new URLSearchParams(formData);
    var queryString = searchParams.toString();
    queryString = "type=text&"+queryString;
    xmlHttpRqst = new XMLHttpRequest( )
    xmlHttpRqst.onload = function(e) {
        data =  JSON.parse(xmlHttpRqst.response);
        goPage(pno=1, psize=20)
    }
    xmlHttpRqst.open( "GET", "/?" + queryString);
    xmlHttpRqst.send();
}

function sumbit_form_graph() {
    var form = document.getElementById("form_graph");
    var formData = new FormData(form);
    var searchParams = new URLSearchParams(formData);
    var queryString = searchParams.toString();
    queryString = "type=graph&"+queryString;
    var res = queryString.split("&")
    for (i=0; i<res.length; i++) {
        if (res[i].startsWith("summary_level")) {
            var level = res[i].split('=')[1]
            update_graph(level)
        }
    }
}

