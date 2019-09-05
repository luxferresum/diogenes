// All used by the pages/firstrun.html page

const {ipcRenderer} = require('electron')
const {dialog} = require('electron').remote
const path = require('path');
const fs = require('fs');

dioSettingsDir = ipcRenderer.sendSync('getsettingsdir')
dioSettingsFile = path.join(dioSettingsDir, 'diogenes.prefs')

let dbs = ['PHI', 'TLG', 'DDP', 'TLL_PDF', 'OLD_PDF']

function setPath(dbName, folderPath) {
    if(typeof folderPath === "undefined") {
        return
    }
    writeToSettings(dbName, folderPath)
    showPath(dbName, folderPath)
    readyDoneButton()
}

function writeToSettings (dbName, folderPath) {
    // check if folderPath is defined.
    try {
        data = fs.readFileSync(dioSettingsFile, 'utf8')
    } catch(e) {
        data = '# Created by electron'
    }
    let db_l = dbName.toLowerCase()
    let newLine = `${db_l}_dir "${folderPath}"`
    let re = new RegExp(`^${db_l}_dir.*$`, 'm')
    let newData
    if(re.test(data)) {
        newData = data.replace(re, newLine)
    } else {
        newData = `${data}\n${newLine}`
    }
    fs.writeFileSync(dioSettingsFile, newData)
}

function showPath(dbName, folderPath) {
    document.getElementById(`${dbName}path`).innerHTML = folderPath

    checkmark = document.getElementById(`${dbName}ok`)
    if(fs.existsSync(`${folderPath}/authtab.dir`) || fs.existsSync(`${folderPath}/AUTHTAB.DIR`) || dbName == 'TLL_PDF' || dbName == 'OLD_PDF') {
        checkmark.innerHTML = '✓'
        checkmark.classList.remove('warn')
        checkmark.classList.add('valid')
    } else {
        checkmark.innerHTML = '✕ No authtab.dir found; this doesn\'t look like a correct database location'
        checkmark.classList.remove('valid')
        checkmark.classList.add('warn')
    }
}

function readyDoneButton() {
    let anyset = 0
    for(let i = 0; i < dbs.length; i++) {
        let d = `${dbs[i]}path`
        if(document.getElementById(d).innerHTML.length > 0) {
            anyset = 1
        }
    }

    if(anyset) {
        document.getElementById('donesection').style.display = 'block'
    }
}

function bindClickEvent(dbName) {
    var prop
    if (dbName == 'OLD_PDF') {
        prop = 'openFile';
    }
    else {
        prop = 'openDirectory';
    }

    document.getElementById(`${dbName}button`).addEventListener('click', () => {
        setPath(dbName, dialog.showOpenDialog({
            title: `Set ${dbName} location`,
            properties: [prop]
        }))
    })
}

function firstrunSetup() {
    // Create settings dir, if necessary
    if(!fs.existsSync(dioSettingsDir)) {
        fs.mkdirSync(dioSettingsDir)
    }

    readyDoneButton()

    document.getElementById('done').addEventListener('click', () => {
        window.location.href = `http://localhost:` + ipcRenderer.sendSync('getport')
    })

    // Read existing db settings
    try {
        data = fs.readFileSync(dioSettingsFile, 'utf8')
    } catch(e) {
        data = null
    }

    for(let i = 0; i < dbs.length; i++) {
        let db = dbs[i]

        bindClickEvent(db)

        if(data === null) {
            continue
        }

        let db_l = db.toLowerCase()
        let re = new RegExp(`^${db_l}_dir\\s+"?(.*?)"?$`, 'm')
        let ar = re.exec(data)
        if(ar) {
            showPath(db, ar[1])
        }
    }
}

function isFirstRunPage() {
    // Only load on the first run page
    if(document.getElementById('firstrunpage') !== null) {
        firstrunSetup()
    }
}

window.addEventListener('load', isFirstRunPage, false)

// Select folder for XML export

function setXMLPath (path) {
    if (path) {
        var event = new CustomEvent('XMLPathResponse', { detail: path });
        document.dispatchEvent(event)
    }
}

function exportPathPick () {
    setXMLPath(dialog.showOpenDialog({
        title: 'Set location for XML directory',
        properties: ['openDirectory']
    }))
}

document.addEventListener('XMLPathRequest', exportPathPick, false)

// Select file for File Save

function saveFile () {
    var path = dialog.showSaveDialog({title: 'Save File Location', defaultPath: 'diogenes-output.html'});
    if (path) {
        ipcRenderer.send('saveFileResponse', path)
    }
}

ipcRenderer.on('saveFileRequest', (event, message) => {
    console.log('Saving file ...');
    saveFile();
});

// Select file for Print to PDF

function printPDF (win) {
    var path = dialog.showSaveDialog({title: 'PDF File Location', defaultPath: 'diogenes-print.pdf'});
    if (path) {
        ipcRenderer.send('printPDFResponse', path)
    }
}

ipcRenderer.on('printPDFRequest', (event, message) => {
    console.log('Printing to PDF ...');
    printPDF();
});

// Open selected links using system default app (e.g. PDFs).

const shell = require('electron').shell;
document.addEventListener('openWithExternal', openWithExternal, false)

function openWithExternal (e) {
    var link = window.location.protocol + '//' + window.location.hostname + ':' + window.location.port + '/' + e.detail;

    console.log('Opening ' + link);

    // Electron can't open PDFs (yet).
    // const { BrowserWindow } = require('electron').remote
    // let win = new BrowserWindow()
    // win.loadURL(link)

    shell.openExternal(link);
}

// Select location to save TLL PDFs prior to download

function TLLPath () {
    // This needs to agree with value in tll-pdf-download.pl
    var dirname = 'tll-pdfs'

    var ok = dialog.showMessageBox({
        type: 'question',
        buttons: ['Cancel', 'OK'],
        defaultId: 0,
        title: 'Continue?',
        message: 'Do you want to go ahead and download the PDFs of the Thesaurus Linguae Latinae?',
        detail: 'Retrieving these large files from the website of the Bayerische Akademie der Wissenschaften may take quite a long time. Click OK to select a location for the new folder.'
    })
    if (ok == 1) {
        var folder = dialog.showOpenDialog({
            title: 'Location for TLL PDF download',
            properties: ['openDirectory']
        })
        if (folder) {
            folder = path.join(folder[0], dirname)
            writeToSettings('TLL_PDF', folder)
            ipcRenderer.send('TLLPathResponse', folder)
            console.log('TLL download path set to ' + folder);
        }
    }
}

ipcRenderer.on('TLLPathRequest', (event, message) => {
    TLLPath();
});


//console.log('preload done');
