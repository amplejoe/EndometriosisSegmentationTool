/*
 * File: fileUpload.js
 * Created: Saturday, 3rd April 2021 4:14:18 am
 * Author: Andreas (amplejoe@gmail.com)
 * -----
 * Last Modified: Saturday, 3rd April 2021 4:16:01 am
 * Modified By: Andreas (amplejoe@gmail.com)
 * -----
 * Copyright (c) 2021 Klagenfurt University
 *
 */

const fileUpload = document.getElementById("video-upload-input");

let activateUploadButton = (value) => {
    let b = document.querySelector("#video-upload-button");
    b.disabled = !value;
}

let showUserInfo = (msg) => {
    let i = document.querySelector("#video-upload-info");
    i.innerHTML = msg;
}

if (fileUpload) {
    fileUpload.addEventListener("change", event => {
        if (event.target.files.length == 0) {
            activateUploadButton(false);
            showUserInfo("");
            return;
        }
        const file = event.target.files[0];
        console.log(file);

        // check if video is valid
        const videoEl = document.createElement("video");
        videoEl.src = window.URL.createObjectURL(file);

        videoEl.onloadedmetadata = event => {
            window.URL.revokeObjectURL(videoEl.src);
            const { name, type } = file;
            const { videoWidth, videoHeight } = videoEl;

            console.log(`Filename: ${name} - Type: ${type} - Size: ${videoWidth}px x ${videoHeight}px`);
            // activate upload button
            showUserInfo("");
            activateUploadButton(true);
        }

        videoEl.onerror = () => {
            let msg = 'Please upload a video file!';
            // console.log(msg);
            showUserInfo(msg);
            activateUploadButton(false);
            return;
        }
    });
}
