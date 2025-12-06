/**
 * BLE Tic-Tac-Toe Client for micro:bit
 */

let connected = false
let boardStr = "........."
let cursorIndex = 0
let myTurn = false
let gameResult = ""
let isSelectingMode = true // Start in selection mode
let isWaitingForResponse = false
let myPlayerSymbol = "X" // Default X, updated on start

// --- Initial Setup ---
bluetooth.startUartService()
basic.showIcon(IconNames.Heart)

// --- Bluetooth Events ---
bluetooth.onBluetoothConnected(function () {
    connected = true
    basic.showIcon(IconNames.Yes)
    pause(1000)
    // Show Selection Menu immediately after connection
    showSelectionMenu()
})

bluetooth.onBluetoothDisconnected(function () {
    connected = false
    basic.showIcon(IconNames.No)
})

// Handle incoming data
bluetooth.onUartDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    let receivedLine = bluetooth.uartReadUntil(serial.delimiters(Delimiters.NewLine))
    // Protocol:
    // BOARD:xxxxxxxxx
    // RESULT:WIN/LOSE/DRAW
    // RESET

    if (receivedLine.includes("BOARD:")) {
        boardStr = receivedLine.substr(6, 9)
        // Switch to Game Mode if receiving board
        if (isSelectingMode) {
            isSelectingMode = false
        }

        isWaitingForResponse = false // Response received

        // If current cursor is on an occupied cell, move to the first empty one
        if (boardStr.charAt(cursorIndex) != ".") {
            for (let i = 0; i < 9; i++) {
                if (boardStr.charAt(i) == ".") {
                    cursorIndex = i
                    break
                }
            }
        }
        renderBoard()
    } else if (receivedLine.includes("RESULT:")) {
        isWaitingForResponse = false // Response received
        // Format: RESULT:STATUS:1,2,3 or RESULT:STATUS
        let parts = receivedLine.split(":")
        gameResult = parts[1] // WIN, LOSE, DRAW

        let blinkIndices: number[] = []
        if (parts.length > 2) {
            let indiciesStr = parts[2].split(",")
            for (let s of indiciesStr) {
                blinkIndices.push(parseInt(s))
            }
        }

        if (blinkIndices.length > 0) {
            blinkWinnerLine(blinkIndices)
        }

        showResult()
    } else if (receivedLine.includes("RESET")) {
        // Back to selection mode
        boardStr = "........."
        gameResult = ""
        isSelectingMode = true
        showSelectionMenu()
    }
})

// --- Control Logic ---

// Button A
input.onButtonPressed(Button.A, function () {
    if (!connected) return

    if (isSelectingMode) {
        // Select P1 (First)
        bluetooth.uartWriteString("START_P1\n")
        basic.showString("1")
        myPlayerSymbol = "X"
        isSelectingMode = false // Wait for Board
    } else if (gameResult != "") {
        // Ignore A in Result screen? Or let it do nothing.
    } else {
        // Game Mode: Move Cursor
        if (isWaitingForResponse) return // Lock input while waiting

        // Skip occupied cells and find the next empty one
        let originalIndex = cursorIndex
        for (let i = 0; i < 9; i++) {
            cursorIndex = (cursorIndex + 1) % 9
            if (boardStr.charAt(cursorIndex) == ".") {
                break
            }
        }
        renderBoard()
    }
})

// Button B
input.onButtonPressed(Button.B, function () {
    if (!connected) return

    if (isSelectingMode) {
        // Select P2 (Second)
        bluetooth.uartWriteString("START_P2\n")
        basic.showString("2")
        myPlayerSymbol = "O"
        isSelectingMode = false // Wait for Board
        return
    }

    if (gameResult != "") {
        // Reset game
        bluetooth.uartWriteString("RESET\n")
        return
    }

    // Game Mode: Select / Confirm
    if (isWaitingForResponse) return // Lock input while waiting

    isWaitingForResponse = true

    // Feedback: Blink strongly at selection to indicate confirmation
    let x = (cursorIndex % 3) + 1
    let y = Math.floor(cursorIndex / 3) + 1

    let brightness = (myPlayerSymbol == "X") ? 255 : 50

    led.plotBrightness(x, y, brightness)
    pause(100)
    led.plotBrightness(x, y, 0)
    pause(100)
    led.plotBrightness(x, y, brightness) // Leave it ON

    // Send Move: MOVE:N
    bluetooth.uartWriteString("MOVE:" + cursorIndex + "\n")
})

// Button A+B: Force Reset
input.onButtonPressed(Button.AB, function () {
    if (!connected) return
    bluetooth.uartWriteString("RESET\n")
})

// --- Display Logic ---

function showSelectionMenu() {
    basic.showString("?")
    // ideally show "A=1 B=2" scrolling
}

// 5x5 Matrix
// 0,0  1,0  2,0  3,0  4,0
// 0,1  [1,1][2,1][3,1] 4,1
// 0,2  [1,2][2,2][3,2] 4,2
// 0,3  [1,3][2,3][3,3] 4,3
// 0,4  1,4  2,4  3,4  4,4
// Board is in center 3x3 (offset x=1, y=1)

function renderBoard() {
    if (isSelectingMode) return

    basic.clearScreen()
    for (let i = 0; i < 9; i++) {
        let mark = boardStr.charAt(i)
        let x = (i % 3) + 1
        let y = Math.floor(i / 3) + 1

        // Draw Mark
        if (mark == "X") {
            led.plotBrightness(x, y, 255) // Bright
        } else if (mark == "O") {
            led.plotBrightness(x, y, 50)  // Dim (to distinguish)
        } else {
            // Empty
            led.plotBrightness(x, y, 0)
        }
    }
}

function blinkWinnerLine(indices: number[]) {
    // Blink 3 times (approx 2 seconds total)
    for (let k = 0; k < 4; k++) {
        // OFF
        for (let idx of indices) {
            let x = (idx % 3) + 1
            let y = Math.floor(idx / 3) + 1
            led.plotBrightness(x, y, 0)
        }
        pause(250)

        // ON
        for (let idx of indices) {
            let x = (idx % 3) + 1
            let y = Math.floor(idx / 3) + 1
            // Use existing board char to determine brightness
            let mark = boardStr.charAt(idx)
            let brightness = 255
            if (mark == "O") brightness = 50
            led.plotBrightness(x, y, brightness)
        }
        pause(250)
    }
}

function showResult() {
    basic.clearScreen()
    if (gameResult == "WIN") {
        basic.showIcon(IconNames.Happy)
    } else if (gameResult == "LOSE") {
        basic.showIcon(IconNames.Sad)
    } else if (gameResult == "DRAW") {
        basic.showIcon(IconNames.Confused)
    }
    pause(2000)
    basic.showString("B=RST")
}

// Background loop for cursor blinking
basic.forever(function () {
    if (!connected || isSelectingMode || gameResult != "") return;

    let x = (cursorIndex % 3) + 1
    let y = Math.floor(cursorIndex / 3) + 1

    // Simple blink for current cursor logic
    if (boardStr.charAt(cursorIndex) == ".") {
        led.plotBrightness(x, y, 150)
        pause(200)
        led.plotBrightness(x, y, 0)
        pause(200)
    } else {
        // If cursor is on occupied cell (shouldn't happen with skip logic, but for safety)
        let currentBright = (boardStr.charAt(cursorIndex) == "X") ? 255 : 50
        led.plotBrightness(x, y, 0)
        pause(100)
        led.plotBrightness(x, y, currentBright)
        pause(300)
    }
})
