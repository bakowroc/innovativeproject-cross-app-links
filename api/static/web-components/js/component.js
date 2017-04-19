(function () {
    var component = {
        element: document.querySelectorAll('#web-component-navbar')[0],
        button: document.querySelectorAll('#web-component-navbar .burger-icon')[0],
        overflow: document.querySelectorAll('#web-component-navbar .component-overflow')[0],
        iframe: document.querySelectorAll('#web-component-navbar iframe')[0],
        use: function () {
            var component = this.element;
            var componentOverflow = this.overflow;

            if (component.className.indexOf("visible") === -1) {
                component.className = component.className.replace(/c-hidden/g, 'visible');
                componentOverflow.className = componentOverflow.className.replace(/c-hidden/g, 'visible');
            } else {
                component.className = component.className.replace(/visible/g, 'c-hidden');
                componentOverflow.className = componentOverflow.className.replace(/visible/g, 'c-hidden');
            }
        },
        request: function () {

            var req = new XMLHttpRequest();
            // creating GET request to yahoo weather API
            req.open('GET', "/api/v2/app", true);
            // sending a request
            req.send();

            req.onreadystatechange = generateHTML;
            var navbar = document.querySelector('.component-overflow .component-ul');

            function generateHTML() {
                if (req.readyState == 4 && req.status == 200) {
                    var listGenerateString = '';
                    var linkArray = JSON.parse(req.responseText);
                    linkArray = linkArray['objects'];
                    for (var i = 0; i < linkArray.length; i++) {
                        listGenerateString += '<li><a href="' + linkArray[i]['link'] + '"> <div class="option-icon"><span class="glyphicon glyphicon-option-horizontal"></span></div><img src="/static/img/app-img/' + linkArray[i]['img_link'] + '.png" /><span class="text">' + linkArray[i]['name'] + '</span></a></li>';
                    }
                    navbar.insertAdjacentHTML('beforeend', listGenerateString);
                }
            }
        },
        start: function () {
            var button = this.button;
            var component = this.element;
            var iframe = this.iframe;
            var componentOverflow = this.overflow;

            //Element which contains web-component
            var pageNavbarHeight = button.parentElement.parentElement.clientHeight;
            //Create square
            component.style.width = parseInt(pageNavbarHeight) + 'px';
            componentOverflow.style.top = parseInt(pageNavbarHeight) + 'px';
            componentOverflow.style.paddingBottom = parseInt(pageNavbarHeight) + 'px';
            button.addEventListener('click', this.use.bind(this));
            this.request();
            component.style.visibility = 'visible';
        }
    };
    //Run
    component.start();

})()