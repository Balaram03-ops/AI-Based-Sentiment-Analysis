/* =====================================================
   AI SENTIMENT ANALYSIS
   REGISTRATION JAVASCRIPT
   ===================================================== */


/* =====================================================
   PASSWORD TOGGLE
   ===================================================== */

function togglePassword(inputId, eyeId) {

    const passwordInput =
        document.getElementById(inputId);

    const eyeIcon =
        document.getElementById(eyeId);


    if (!passwordInput || !eyeIcon) {

        return;

    }


    if (passwordInput.type === "password") {

        passwordInput.type = "text";


        eyeIcon.classList.remove(
            "bi-eye-fill"
        );


        eyeIcon.classList.add(
            "bi-eye-slash-fill"
        );

    }

    else {

        passwordInput.type = "password";


        eyeIcon.classList.remove(
            "bi-eye-slash-fill"
        );


        eyeIcon.classList.add(
            "bi-eye-fill"
        );

    }

}



/* =====================================================
   PASSWORD STRENGTH
   ===================================================== */

const passwordInput =
    document.getElementById("password");

const strengthBar =
    document.getElementById("strengthBar");

const strengthText =
    document.getElementById("strengthText");


if (passwordInput) {

    passwordInput.addEventListener(
        "input",
        function () {

            const password =
                passwordInput.value;


            let strength = 0;


            if (password.length >= 8) {

                strength++;

            }


            if (/[A-Z]/.test(password)) {

                strength++;

            }


            if (/[0-9]/.test(password)) {

                strength++;

            }


            if (/[^A-Za-z0-9]/.test(password)) {

                strength++;

            }


            if (strength === 0) {

                strengthBar.style.width =
                    "0%";

                strengthText.textContent =
                    "Password strength";

            }

            else if (strength === 1) {

                strengthBar.style.width =
                    "25%";

                strengthText.textContent =
                    "Weak password";

            }

            else if (strength === 2) {

                strengthBar.style.width =
                    "50%";

                strengthText.textContent =
                    "Medium password";

            }

            else if (strength === 3) {

                strengthBar.style.width =
                    "75%";

                strengthText.textContent =
                    "Strong password";

            }

            else {

                strengthBar.style.width =
                    "100%";

                strengthText.textContent =
                    "Very strong password";

            }

        }
    );

}



/* =====================================================
   CONFIRM PASSWORD
   ===================================================== */

const confirmPassword =
    document.getElementById(
        "confirmPassword"
    );

const matchMessage =
    document.getElementById(
        "matchMessage"
    );


function checkPasswordMatch() {

    if (
        !confirmPassword ||
        !matchMessage ||
        !passwordInput
    ) {

        return;

    }


    if (
        confirmPassword.value === ""
    ) {

        matchMessage.textContent =
            "";

        return;

    }


    if (
        confirmPassword.value ===
        passwordInput.value
    ) {

        matchMessage.textContent =
            "✓ Passwords match";

        matchMessage.style.color =
            "#4ade80";

    }

    else {

        matchMessage.textContent =
            "✕ Passwords do not match";

        matchMessage.style.color =
            "#f87171";

    }

}


if (confirmPassword) {

    confirmPassword.addEventListener(
        "input",
        checkPasswordMatch
    );

}


if (passwordInput) {

    passwordInput.addEventListener(
        "input",
        checkPasswordMatch
    );

}



/* =====================================================
   FORM VALIDATION
   ===================================================== */

const registerForm =
    document.getElementById(
        "registerForm"
    );


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        function (event) {


            const password =
                document.getElementById(
                    "password"
                ).value;


            const confirm =
                document.getElementById(
                    "confirmPassword"
                ).value;


            if (password !== confirm) {

                event.preventDefault();


                alert(
                    "Passwords do not match."
                );


                return;

            }


            if (password.length < 6) {

                event.preventDefault();


                alert(
                    "Password must contain at least 6 characters."
                );


                return;

            }

        }
    );

}



/* =====================================================
   MOUSE PARALLAX FOR AI VISUAL
   ===================================================== */

const aiVisual =
    document.querySelector(
        ".ai-visual"
    );


const aiBag =
    document.querySelector(
        ".ai-bag"
    );


if (
    aiVisual &&
    aiBag &&
    window.innerWidth > 768
) {

    aiVisual.addEventListener(
        "mousemove",
        function (event) {


            const rect =
                aiVisual.getBoundingClientRect();


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
                centerX) * 8;


            const rotateX =
                ((centerY - y) /
                centerY) * 6;


            aiBag.style.transform =

                `translateY(-10px)
                 rotateX(${rotateX}deg)
                 rotateY(${rotateY}deg)`;

        }
    );


    aiVisual.addEventListener(
        "mouseleave",
        function () {

            aiBag.style.transform =
                "";

        }
    );

}
