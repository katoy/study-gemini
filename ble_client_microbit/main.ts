/**
 * BLE Tic-Tac-Toe Client for micro:bit (Stateless Protocol)
 */

// --- Global State ---
let connected = false
let boardStr = "........." // Always holds the current board state
let cursorIndex = 0
let myPlayerSymbol = "X"   // "X" or "O"
let gameResult = ""        // "ONGOING", "WIN", "LOSE", "DRAW"
let isSelectingMode = true // True when showing the initial player selection menu
let isWaitingForResponse = false // Lock input while waiting for server

// --- Initial Setup ---
bluetooth.startUartService()
basic.showIcon(IconNames.Heart)

// --- Bluetooth Event Handlers ---

bluetooth.onBluetoothConnected(function () {
    connected = true
    isSelectingMode = true
    gameResult = ""
    boardStr = "........."
    myPlayerSymbol = "X"
    basic.showIcon(IconNames.Yes)
    pause(1000)
    showSelectionMenu()
})

bluetooth.onBluetoothDisconnected(function () {
    connected = false
    isWaitingForResponse = false
    basic.showIcon(IconNames.No)
})

// Handle all incoming data from the server
bluetooth.onUartDataReceived(serial.delimiters(Delimiters.NewLine), function () {
    if (!connected) return

    let receivedLine = bluetooth.uartReadUntil(serial.delimiters(Delimiters.NewLine)).trim()
    if (receivedLine == "") return

    if (receivedLine.substr(0, 7) == "RESULT:") {
        // This is the second message in a game-over sequence
        // Format: RESULT:<GAME_RESULT>:<WIN_LINE>
        let parts = receivedLine.substr(7).split(":")
        if (parts.length < 1) return

        gameResult = parts[0]

        // Handle Game Over display logic
        let winLineStr = (parts.length > 1) ? parts[1] : ""
        if (winLineStr != "") {
            let blinkIndices: number[] = []
            let indiciesStr = winLineStr.split(",")
            for (let s of indiciesStr) {
                blinkIndices.push(parseInt(s))
            }
            if (blinkIndices.length > 0) {
                // Blink the winning line
                blinkWinnerLine(blinkIndices)
                // Show the final board with the line for a moment
                renderBoard()
                for (let idx of blinkIndices) {
                    let mark = boardStr.charAt(idx)
                    led.plotBrightness((idx % 3) + 1, Math.floor(idx / 3) + 1, mark == "X" ? 255 : 50)
                }
                pause(1500)
            }
        }
        showResult() // Then show result icon (Happy, Sad, etc.)

    } else {
        // This is a standard board update
        // Format: <BOARD_STATE>:<GAME_RESULT>:<WIN_LINE>
        let parts = receivedLine.split(":")
        if (parts.length < 2) return

        // 1. Update Board State
        boardStr = parts[0]
        // 2. Update Game Result (will be "ONGOING" unless it's a direct start->gameover)
        gameResult = parts[1]

        // We are no longer waiting for a response for our move
        isWaitingForResponse = false
        if (isSelectingMode) {
            isSelectingMode = false // First response from server, switch to game mode
        }

        renderBoard()

        // If the game is ongoing, find the next available spot for the cursor
        if (gameResult == "ONGOING") {
            if (boardStr.charAt(cursorIndex) != ".") {
                for (let i = 0; i < 9; i++) {
                    if (boardStr.charAt(i) == ".") {
                        cursorIndex = i
                        break
                    }
                }
            }
            renderBoard()
        }
    }
})


// --- Control Logic ---

// Button A: Move cursor / Select Player 1 (X)
input.onButtonPressed(Button.A, function () {
    if (!connected || isWaitingForResponse) return

    if (isSelectingMode) {
        // Select Player 1 (X, goes first)
        myPlayerSymbol = "X"
        isWaitingForResponse = true
        bluetooth.uartWriteString("START:" + myPlayerSymbol + "\n")
        basic.showString("1")
    } else if (gameResult != "" && gameResult != "ONGOING") {
        // In result screen, do nothing
    } else {
        // Game Mode: Move Cursor to the next empty spot
        for (let i = 0; i < 9; i++) {
            cursorIndex = (cursorIndex + 1) % 9
            if (boardStr.charAt(cursorIndex) == ".") {
                break
            }
        }
        renderBoard()
    }
})

// Button B: Confirm move / Select Player 2 (O) / Reset
input.onButtonPressed(Button.B, function () {
    if (!connected || isWaitingForResponse) return

    if (isSelectingMode) {
        // Select Player 2 (O, goes second)
        myPlayerSymbol = "O"
        isWaitingForResponse = true
        bluetooth.uartWriteString("START:" + myPlayerSymbol + "\n")
        basic.showString("2")
        return
    }

    if (gameResult != "" && gameResult != "ONGOING") {
        // Game is over, B acts as Reset
        resetGame()
        return
    }

    // Game Mode: Confirm move
    if (boardStr.charAt(cursorIndex) == ".") {
        isWaitingForResponse = true
        
        // Feedback: Show selection
        let x = (cursorIndex % 3) + 1
        let y = Math.floor(cursorIndex / 3) + 1
        led.plotBrightness(x, y, myPlayerSymbol == "X" ? 255 : 50)
        pause(200)

        // Send Move Command: MOVE:<INDEX>:<SYMBOL>:<BOARD>
        let command = "MOVE:" + cursorIndex + ":" + myPlayerSymbol + ":" + boardStr + "\n"
        bluetooth.uartWriteString(command)
    }
})

// Button A+B: Force Reset
input.onButtonPressed(Button.AB, function () {
    if (!connected) return
    resetGame()
})

function resetGame() {
    isWaitingForResponse = false
    isSelectingMode = true
    gameResult = ""
    boardStr = "........."
    showSelectionMenu()
}


// --- Display Logic ---

function showSelectionMenu() {
    basic.clearScreen()
    basic.showString("?")
}

// Renders the board based on the global 'boardStr'
function renderBoard() {
    if (isSelectingMode) return
    basic.clearScreen()
    for (let i = 0; i < 9; i++) {
        let mark = boardStr.charAt(i)
        let x = (i % 3) + 1
        let y = Math.floor(i / 3) + 1

        if (mark == "X") {
            led.plotBrightness(x, y, 255) // Bright
        } else if (mark == "O") {
            led.plotBrightness(x, y, 50)  // Dim
        }
    }
}

// Blinks the winning line
function blinkWinnerLine(indices: number[]) {
    for (let k = 0; k < 4; k++) {
        // OFF
        for (let idx of indices) {
            led.plotBrightness((idx % 3) + 1, Math.floor(idx / 3) + 1, 0)
        }
        pause(250)
        // ON
        for (let idx of indices) {
            let mark = boardStr.charAt(idx)
            led.plotBrightness((idx % 3) + 1, Math.floor(idx / 3) + 1, mark == "X" ? 255 : 50)
        }
        pause(250)
    }
}

// Shows the final result icon
function showResult() {
    basic.clearScreen()
    if (gameResult == "WIN") {
        basic.showIcon(IconNames.Happy)
    } else if (gameResult == "LOSE") {
        basic.showIcon(IconNames.Sad)
    } else if (gameResult == "DRAW") {
        basic.showIcon(IconNames.Asleep)
    }
    pause(2000)
    basic.showString("B=RST")
}

// Background loop for cursor blinking
basic.forever(function () {
    // Blink cursor only in game mode and if the spot is empty
    if (!connected || isSelectingMode || isWaitingForResponse || gameResult != "ONGOING") return
    
    if (boardStr.charAt(cursorIndex) == ".") {
        let x = (cursorIndex % 3) + 1
        let y = Math.floor(cursorIndex / 3) + 1
        // Toggle LED
        led.toggle(x, y)
        pause(300)
    }
})