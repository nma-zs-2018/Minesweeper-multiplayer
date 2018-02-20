/**
 MineSweeper.js
 Author: Michael C. Butler
 Url: https://github.com/michaelbutler/minesweeper
 */

var MineSweeper;

jQuery(function ($) {
    'use strict';
    // "Static Constants"
    var STATE_UNKNOWN = 'unknown',
        STATE_OPEN = 'open',
        STATE_NUMBER = 'number',
        STATE_EXPLODE = 'explode',
        STATE_EXPLODE_TRIGGERED = 'triggered';
    var INT_STATE_EXPLODE = 99,
        INT_EXPLODE_TRIGGERED = 98;
    var LEFT_MOUSE_BUTTON = 1,
        RIGHT_MOUSE_BUTTON = 3;

    MineSweeper = function () {
        // prevent namespace pollution
        if (!(this instanceof MineSweeper)) {
            throw 'Invalid use of Minesweeper';
        }
        var msObj = this;
        this.options = {};
        this.grid = [];
        this.pathToCellToucher = '/static/minesweeper/js/cell_toucher.js';

        this.init = function (socket) {
            msObj.socket = socket;
            var msUI = $('#minesweeper');
            // insert progress animation before the grid
            if ($('.ajax-loading').length < 1) {
                msUI.before(
                '<div class="invisible ajax-loading"></div>'
                );
            }
            msObj.initWorkers(msObj.pathToCellToucher);
            msObj.initHandlers(msUI);
            msObj.board = $('.board-wrap');
            msObj.board.attr('unselectable', 'on')
                .css('UserSelect', 'none')
                .css('MozUserSelect', 'none');
            return msObj;
        };
        this.createBoard = function(board){
             var width = msObj.options.boardSize[0],
                height = msObj.options.boardSize[1],
                x,
                y,
                z = 0;

            msObj.grid = [];
            for (y = 0; y < height; y++) {
                msObj.grid[y] = [];
                for (x = 0; x < width; x++) {
                    msObj.grid[y][x] = {
                        'state': STATE_UNKNOWN,
                        'number': 0,
                        'x': x,
                        'y': y
                    };
                    if(board[x][y] === 0) {
                        msObj.grid[y][x]['state'] = STATE_OPEN;
                    }
                    else if(board[x][y] <= 9) {
                        msObj.grid[y][x]['state'] = STATE_NUMBER;
                        msObj.grid[y][x]['number'] = board[x][y];
                    }
                    else if(board[x][y] === INT_STATE_EXPLODE) {
                        msObj.grid[y][x]['state'] = STATE_EXPLODE;
                    }
                    else if(board[x][y] === INT_EXPLODE_TRIGGERED) {
                        msObj.grid[y][x]['state'] = STATE_EXPLODE_TRIGGERED;
                    }
                }
            }

            // Insert the board cells in DOM]
            msObj.board.html('');
            for (y = 0; y < height; y++) {
                var row = $('<ul class="row" data-index=' + y + '></ul>');
                for (x = 0; x < width; x++) {
                    var cell;
                    row.append(
                        '<li class="cell" data-coord="' + [x, y].join(',') + '" data-x=' + x +
                        ' data-y=' + y + '>x</li>'
                    );
                    cell = row.find('.cell:last');
                    msObj.drawCell(cell);
                }
                msObj.board.append(row);
            }
        };

        /**
         *
         * @param taskType get_adjacent, touch_adjacent, or calc_win
         * @param payload number or object with {x: ?, y: ?}
         */
        this.callWorker = function(taskType, payload) {
            console.log("ASD");
            $('.ajax-loading').removeClass('invisible');
            var job = {
                type: taskType, // message type
                grid: msObj.grid
            };
            if (typeof payload === 'number') {
                job.mines = payload;
            } else if (typeof payload === 'object'){
                job.x = payload.x;
                job.y = payload.y;
            }
            msObj.worker.postMessage(JSON.stringify(job));
        };

        this.initWorkers = function (wPath) {
            if (window.Worker) {
                // Create a background web worker to process the grid "painting" with a stack
                msObj.worker = new Worker(wPath);
                msObj.worker.onmessage = function (e) {
                    var data = JSON.parse(e.data);
                    msObj.handleWorkerMessage(data);
                };
            } else {
                alert(
                    'Minesweeper requires Web Worker support. ' +
                    'See https://browser-update.org/update.html'
                );
            }
        };

        this.load = function(options){
            msObj.started = options.started;
            msObj.ended = options.ended;
            msObj.turn = options.turn;

            var game = options.game;

            msObj.options.boardSize = [game.n, game.m];
            msObj.options.numMines = game.mines;

            if(!msObj.timer){
                msObj.startTimer();
            }

            msObj.resetDisplays(game);
            msObj.createBoard(game.board);
            msObj.redrawBoard();
            if(game.fail !== 'None' || game.won === 1){
                var width = msObj.options.boardSize[0],
                    height = msObj.options.boardSize[1],
                    x,
                    y;

                for (y = 0; y < height; y++) {
                    for (x = 0; x < width; x++) {
                        var obj = msObj.grid[y][x],
                            cell = msObj.getJqueryObject(x,y);
                        if (obj.state === STATE_EXPLODE || obj.state === STATE_EXPLODE_TRIGGERED) {
                            cell.removeClass('ui-icon-help')
                                .addClass('ui-icon ui-icon-close blown');
                            if(obj.state !== STATE_EXPLODE_TRIGGERED){
                                cell.removeClass('explode');
                            }
                        } else {
                            cell.addClass('unblown');
                        }
                    }
                }
            }
        };

        this.initHandlers = function (msUI) {
            msUI.on('mousedown', function (ev) {
                if (ev.which === RIGHT_MOUSE_BUTTON) {
                    clearTimeout(msObj.RIGHT_BUTTON_TIMEOUT);
                    msObj.RIGHT_MOUSE_DOWN = true;
                } else if (ev.which === LEFT_MOUSE_BUTTON) {
                    clearTimeout(msObj.LEFT_BUTTON_TIMEOUT);
                    msObj.LEFT_MOUSE_DOWN = true;
                }
            });

            msUI.on('mouseup', function (ev) {
                if (ev.which === RIGHT_MOUSE_BUTTON) {
                    msObj.RIGHT_BUTTON_TIMEOUT = setTimeout(function () {
                        msObj.RIGHT_MOUSE_DOWN = false;
                    }, 50);
                } else if (ev.which === LEFT_MOUSE_BUTTON) {
                    msObj.LEFT_BUTTON_TIMEOUT = setTimeout(function () {
                        msObj.LEFT_MOUSE_DOWN = false;
                    }, 50);
                }
            });

            msUI.on('mousedown','.cell', function (ev) {
                var targ = $(ev.target);
                if ((ev.which === LEFT_MOUSE_BUTTON && msObj.RIGHT_MOUSE_DOWN) ||
                    (ev.which === RIGHT_MOUSE_BUTTON && msObj.LEFT_MOUSE_DOWN)
                ) {
                    var x = targ.attr('data-x') - 1;
                    var ud = targ.parent().prev();
                    var i;

                    for(i = x; i < x + 3; i++) {
                        ud.children('.unknown.[data-x=' + i + ']').addClass('test');
                    }
                    targ.prev('.unknown').addClass('test');
                    targ.next('.unknown').addClass('test');
                    ud = targ.parent().next();
                    for(i = x; i < x + 3; i++) {
                        ud.children('.unknown.[data-x=' + i + ']').addClass('test');
                    }
                }
            });

            msUI.on('mouseup','.cell', function (ev) {
                var targ = $(ev.target);
                if (ev.which === LEFT_MOUSE_BUTTON) {
                    msObj.handleLeftClick(targ);
                }
            });
        };

        this.handleLeftClick = function (cell) {
            var obj = msObj.getCellObj(cell);

            msObj.socket.send("{\"x\": "+obj.x+", \"y\": "+obj.y+"}");
        };

        this.handleWorkerMessage = function (data) {
            if (data.type === 'touch_adjacent' || data.type === 'get_adjacent') {
                msObj.grid = data.grid;
                msObj.redrawBoard();
            } else if (data.type === 'explode') {
                var cell = msObj.getJqueryObject(data.cell.x, data.cell.y);
                msObj.gameOver(cell);
            } else if (data.type === 'log') {
                if (console && console.log) {
                    console.log(data.obj);
                }
            }
            $('.ajax-loading').addClass('invisible');
        };

        // return memory representation for jQuery instance
        this.getCellObj = function (domObj) {
            var gridobj,
                x,
                y;
            try {
                x = parseInt(domObj.attr('data-x'), 10);
                y = parseInt(domObj.attr('data-y'), 10);
                gridobj = msObj.grid[y][x];
            } catch (e) {
                console.warn('Could not find memory representation for:');
                console.log(domObj);
                throw 'Stopped.';
            }

            return gridobj;
        };

        this.getJqueryObject = function (x, y) {
            return msObj.board.find('.cell[data-coord="' + [x, y].join(',') + '"]');
        };

        this.startTimer = function () {
            var timerElement = $('#timer');
            function update() {
                if(msObj.ended !== 0) {
                    timerElement.text(Math.round(msObj.ended - msObj.started));
                    clearInterval(msObj.timer);
                } else{
                    var d = new Date();
                    var t_millis = d.getTime();
                    timerElement.text(Math.round((t_millis - msObj.started * 1000) / 1000));
                }
            }
            update();
            msObj.timer = window.setInterval(function () {
                update();
            }, 1000);
        };

        this.resetDisplays = function (game) {
            $('#mine_flag_display').text(msObj.options.numMines);
            $('#cells_left').text(game.unknown);
            var ended = true;
            if(game.won === 1)
                $('#emoji').text(':)');
            else if(game.fail !== 'None')
                $('#emoji').text(':( ' + game.fail);
            else{
                ended = false;
                $('#emoji').text(':|');
                $('#turn').text(msObj.turn);
            }
            if(ended){
                $('#turn').hide();
                $('#turn_label').hide();
            }
        };

        this.redrawBoard = function () {
            msObj.board.find('li.cell').each(function (ind, cell) {
                msObj.drawCell($(cell));
            });
        };

        this.drawCell = function (x, y) {
            var cell = null,
                gridobj;
            if (x instanceof jQuery) {
                cell = x;
                x = parseInt(cell.attr('data-x'), 10);
                y = parseInt(cell.attr('data-y'), 10);
            } else if (typeof x === 'number' && typeof y === 'number') {
                cell = msObj.getJqueryObject(x, y);
            }

            cell.removeClass().addClass('cell');

            try {
                gridobj = msObj.grid[y][x];
            } catch (e) {
                console.warn('Invalid grid coord: x,y = ' + [x, y].join(','));
                return;
            }
            cell.html('');
            cell.attr('data-number', '');
            switch (gridobj.state) {
                case STATE_UNKNOWN:
                case STATE_OPEN:
                case STATE_EXPLODE:
                    cell.addClass(gridobj.state);
                    break;
                case STATE_EXPLODE_TRIGGERED:
                    cell.addClass(STATE_EXPLODE);
                    break;
                case STATE_NUMBER:
                    cell.addClass('number');
                    cell.html(gridobj.number);
                    cell.attr('data-number', gridobj.number);
                    break;
                default:
                    throw 'Invalid gridobj state: ' + gridobj.state;
            }
        };
    };
});
