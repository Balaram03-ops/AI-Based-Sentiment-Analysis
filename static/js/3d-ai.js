/* =====================================================
   AI SENTIMENT ANALYSIS
   3D AI JAVASCRIPT
   ===================================================== */


/* =====================================================
   DOM READY
   ===================================================== */

document.addEventListener(
    "DOMContentLoaded",
    function () {


        /* =================================================
           LOGIN 3D SCENE
           ================================================= */

        const aiScene =
            document.querySelector(
                ".ai-3d-scene"
            );


        const aiBag =
            document.querySelector(
                ".ai-bag"
            );


        if (aiScene && aiBag) {

            aiScene.addEventListener(
                "mousemove",
                function (event) {

                    const rect =
                        aiScene.getBoundingClientRect();


                    const x =
                        event.clientX -
                        rect.left;


                    const y =
                        event.clientY -
                        rect.top;


                    const centerX =
                        rect.width / 2;


                    const centerY =
                        rect.height / 2;


                    const rotateY =
                        ((x - centerX) /
                        centerX) * 15;


                    const rotateX =
                        ((centerY - y) /
                        centerY) * 15;


                    /*
                       Stop CSS animation temporarily
                       while mouse is controlling the bag.
                    */

                    aiBag.style.animation =
                        "none";


                    aiBag.style.transform =
                        `translateY(-5px)
                         rotateX(${rotateX}deg)
                         rotateY(${rotateY}deg)`;

                }
            );


            aiScene.addEventListener(
                "mouseleave",
                function () {

                    /*
                       Restore original CSS animation.
                    */

                    aiBag.style.animation =
                        "";

                    aiBag.style.transform =
                        "";

                }
            );

        }


        /* =================================================
           LOGIN CARD 3D EFFECT
           ================================================= */

        const loginCard =
            document.querySelector(
                ".login-card"
            );


        if (loginCard) {

            loginCard.addEventListener(
                "mousemove",
                function (event) {

                    const rect =
                        loginCard.getBoundingClientRect();


                    const x =
                        event.clientX -
                        rect.left;


                    const y =
                        event.clientY -
                        rect.top;


                    const rotateY =
                        ((x - rect.width / 2) /
                        rect.width) * 4;


                    const rotateX =
                        ((rect.height / 2 - y) /
                        rect.height) * 4;


                    loginCard.style.transform =
                        `perspective(1000px)
                         rotateX(${rotateX}deg)
                         rotateY(${rotateY}deg)`;

                }
            );


            loginCard.addEventListener(
                "mouseleave",
                function () {

                    loginCard.style.transform =
                        "perspective(1000px) " +
                        "rotateX(0deg) " +
                        "rotateY(0deg)";

                }
            );

        }


        /* =================================================
           HOME 3D CARDS
           ================================================= */

        const aiCards =
            document.querySelectorAll(
                ".ai-3d-card"
            );


        aiCards.forEach(
            function (card) {

                card.addEventListener(
                    "mousemove",
                    function (event) {

                        const rect =
                            card.getBoundingClientRect();


                        const x =
                            event.clientX -
                            rect.left;


                        const y =
                            event.clientY -
                            rect.top;


                        const centerX =
                            rect.width / 2;


                        const centerY =
                            rect.height / 2;


                        const rotateX =
                            ((y - centerY) /
                            centerY) * -4;


                        const rotateY =
                            ((x - centerX) /
                            centerX) * 4;


                        card.style.transform =
                            `perspective(1000px)
                             rotateX(${rotateX}deg)
                             rotateY(${rotateY}deg)
                             translateY(-6px)`;

                    }
                );


                card.addEventListener(
                    "mouseleave",
                    function () {

                        card.style.transform =
                            "perspective(1000px) " +
                            "rotateX(0deg) " +
                            "rotateY(0deg) " +
                            "translateY(0)";

                    }
                );

            }
        );


        /* =================================================
           DASHBOARD 3D CARDS
           ================================================= */

        const dashboardCards =
            document.querySelectorAll(
                ".dashboard-3d-card"
            );


        dashboardCards.forEach(
            function (card) {

                card.addEventListener(
                    "mousemove",
                    function (event) {

                        const rect =
                            card.getBoundingClientRect();


                        const x =
                            event.clientX -
                            rect.left;


                        const y =
                            event.clientY -
                            rect.top;


                        const centerX =
                            rect.width / 2;


                        const centerY =
                            rect.height / 2;


                        const rotateX =
                            ((y - centerY) /
                            centerY) * -5;


                        const rotateY =
                            ((x - centerX) /
                            centerX) * 5;


                        card.style.transform =
                            `perspective(1200px)
                             rotateX(${rotateX}deg)
                             rotateY(${rotateY}deg)
                             translateY(-8px)`;

                    }
                );


                card.addEventListener(
                    "mouseleave",
                    function () {

                        card.style.transform =
                            "perspective(1200px) " +
                            "rotateX(0deg) " +
                            "rotateY(0deg) " +
                            "translateY(0)";

                    }
                );

            }
        );


        /* =================================================
           DASHBOARD HEADER
           ================================================= */

        const dashboardHeader =
            document.getElementById(
                "dashboardHeader"
            );


        if (dashboardHeader) {

            add3DTilt(
                dashboardHeader,
                3,
                4
            );

        }


        /* =================================================
           HISTORY HEADER
           ================================================= */

        const historyHeader =
            document.getElementById(
                "historyHeader"
            );


        if (historyHeader) {

            add3DTilt(
                historyHeader,
                3,
                4
            );

        }


        /* =================================================
           HISTORY SEARCH
           ================================================= */

        const historySearch =
            document.getElementById(
                "historySearch"
            );


        if (historySearch) {

            add3DTilt(
                historySearch,
                2,
                3
            );

        }


        /* =================================================
           HISTORY ITEMS
           ================================================= */

        const historyItems =
            document.querySelectorAll(
                ".history-item-3d"
            );


        historyItems.forEach(
            function (item) {

                item.addEventListener(
                    "mousemove",
                    function (event) {

                        const rect =
                            item.getBoundingClientRect();


                        const x =
                            event.clientX -
                            rect.left;


                        const y =
                            event.clientY -
                            rect.top;


                        const centerX =
                            rect.width / 2;


                        const centerY =
                            rect.height / 2;


                        const rotateX =
                            ((y - centerY) /
                            centerY) * -2;


                        const rotateY =
                            ((x - centerX) /
                            centerX) * 2;


                        item.style.transform =
                            `perspective(1000px)
                             rotateX(${rotateX}deg)
                             rotateY(${rotateY}deg)
                             translateX(4px)
                             translateZ(10px)`;

                    }
                );


                item.addEventListener(
                    "mouseleave",
                    function () {

                        item.style.transform =
                            "perspective(1000px) " +
                            "rotateX(0deg) " +
                            "rotateY(0deg) " +
                            "translateX(0) " +
                            "translateZ(0)";

                    }
                );

            }
        );

    }
);


/* =====================================================
   GENERIC 3D TILT FUNCTION
   ===================================================== */

function add3DTilt(
    element,
    rotateXAmount,
    rotateYAmount
) {


    if (!element) {
        return;
    }


    element.addEventListener(
        "mousemove",
        function (event) {


            const rect =
                element.getBoundingClientRect();


            const x =
                event.clientX -
                rect.left;


            const y =
                event.clientY -
                rect.top;


            const centerX =
                rect.width / 2;


            const centerY =
                rect.height / 2;


            const rotateX =
                ((y - centerY) /
                centerY) *
                -rotateXAmount;


            const rotateY =
                ((x - centerX) /
                centerX) *
                rotateYAmount;


            element.style.transform =
                `perspective(1200px)
                 rotateX(${rotateX}deg)
                 rotateY(${rotateY}deg)
                 translateY(-4px)`;

        }
    );


    element.addEventListener(
        "mouseleave",
        function () {

            element.style.transform =
                "perspective(1200px) " +
                "rotateX(0deg) " +
                "rotateY(0deg) " +
                "translateY(0)";

        }
    );

}


/* =====================================================
   PASSWORD SHOW / HIDE
   ===================================================== */

function togglePassword() {


    const password =
        document.getElementById(
            "loginPassword"
        );


    const eye =
        document.getElementById(
            "loginEye"
        );


    if (!password || !eye) {

        return;

    }


    if (
        password.type ===
        "password"
    ) {


        password.type =
            "text";


        eye.classList.remove(
            "bi-eye"
        );


        eye.classList.add(
            "bi-eye-slash"
        );


    }

    else {


        password.type =
            "password";


        eye.classList.remove(
            "bi-eye-slash"
        );


        eye.classList.add(
            "bi-eye"
        );

    }

}