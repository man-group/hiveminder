function onClickRotate(event, changeHeading) {
    var volantTag = $(event.target).parent().parent();

    var volantId = volantTag.attr("volant_id");
    var heading = changeHeading(parseInt(volantTag.attr("heading")));
    
    volantTag.attr("heading", heading);
    
    applyMove(0, game, {entity: volantId,
                        command: heading});

    $("#human-input").hide();
    hideControls();
}

function onClickFlower(event) {
    var volantTag = $(event.target).parent().parent();

    applyMove(0, game, {entity: volantTag.attr("volant_id"),
                        command: "flower"});

    $("#human-input").hide();
    hideControls();
}

function onClickHive(event) {
    var volantTag = $(event.target).parent().parent();

    applyMove(0, game, {entity: volantTag.attr("volant_id"),
                        command: "create_hive"});

    $("#human-input").hide();
    hideControls();
}

function addControls(controls_tag) {
    anticlockwise = $('<button/>', {class: "anticlockwise"}).appendTo(controls_tag);
    anticlockwise.click(function(event){
        return onClickRotate(event, function(heading) {
                                        switch(heading) {
                                            case 0:
                                                return -60;
                                            case -60:
                                                return -120;
                                            case -120:
                                                return 180;
                                            case 180:
                                                return 120;
                                            case 120:
                                                return 60;
                                            case 60:
                                                return 0;
                                        }            
                                    });
    });

    skip = $('<button/>', {class: "skip"}).appendTo(controls_tag);
    skip.click(function(event){
        return onClickRotate(event, function(heading) {
            return heading;
        });
    });

    clockwise = $('<button/>', {class: "clockwise"}).appendTo(controls_tag);
    clockwise.click(function(event){
        return onClickRotate(event, function(heading) {
                                        switch(heading) {
                                            case 0:
                                                return 60;
                                            case 60:
                                                return 120;
                                            case 120:
                                                return 180;
                                            case 180:
                                                return -120;
                                            case -120:
                                                return -60;
                                            case -60:
                                                return 0;
                                        }            
                                    });
    });
}

function addTile(col_tag, attrs) {
    return $('<div/>', attrs).appendTo(col_tag);
}
   

function addCell(col_tag, attrs, controls) {
    var tile_tag = addTile(col_tag, $.extend(attrs, {volant_id: "",
                                                     heading: "",
                                                     energy: ""}));
    
    var scenary_layer_tag = $('<div/>', {class: "scenary layer"}).appendTo(tile_tag);
    
    var scenary_ometer_tag = $('<div/>', {class: "ometer"}).appendTo(scenary_layer_tag);
    var scenary_ometer_bar_tag = $('<div/>', {class: "bar nectar"}).appendTo(scenary_ometer_tag);
    
    $('<div/>', {class: "crash layer"}).appendTo(tile_tag);
    
    var bee_layer_tag = $('<div/>', {class: "bee layer"}).appendTo(tile_tag);
    
    var bee_ometer_tag = $('<div/>', {class: "ometer"}).appendTo(bee_layer_tag);
    var bee_ometer_bar_tag = $('<div/>', {class: "bar"}).appendTo(bee_ometer_tag);
    
    if (controls) {
        var bee_controls_tag = $('<div/>', {class: "controls"}).appendTo(bee_layer_tag);
        
        $('<button/>', {class: "hivecmd"}).appendTo(bee_controls_tag).click(onClickHive);
        addControls(bee_controls_tag);
    }
    
    var seed_layer_tag = $('<div/>', {class: "seed layer"}).appendTo(tile_tag);
    
    if (controls) {
        var seed_controls_tag = $('<div/>', {class: "controls"}).appendTo(seed_layer_tag);
    
        $('<button/>', {class: "flowercmd"}).appendTo(seed_controls_tag).click(onClickFlower);
        addControls(seed_controls_tag);
    }
}

function neighbourColour(neighbour, num_algos) {
    if (neighbour <= 3) {
        return neighbour;
    } else if (neighbour >= (num_algos - 3)) {
        return 7 + neighbour - num_algos;
    }
}

function drawBoard() {
    var board = $("#board");
    board.empty();
    
    var num_algos = listAlgos().length;

    var tile = { width: 60,
                 height: 55, // include css margin
                 hoverlap: 48,
                 voverlap: 27 };

    var multiplayer = $("#multiplayer").is(':checked');
    var boardwidth = parseInt($("#boardwidth")[0].value);
    var boardheight = parseInt($("#boardheight")[0].value);
                 
    board.width((boardwidth + 1)*tile.hoverlap + tile.width);
    board.height((boardheight + 2)*tile.height);
    
    var start = 0;
    var end = boardwidth;
    
    if (multiplayer) {
        start = -1;
        end = boardwidth + 1;
    }

    for(var i=start; i<end; ++i) {
        var offset = 0;
        if (i % 2 != 0) {
            offset = tile.voverlap;
        }

        var col_tag = $('<div/>', {id: "col" + i,
                                   class: "col",
                                   style: "left:" + ((i+1)*tile.hoverlap) + "px;top:" + offset + "px;",
                                   }).appendTo('#board');
        if (multiplayer && (i >= 0) && (i < boardwidth)) {
            var neighbour = (num_algos + 3) % num_algos;
            addCell(col_tag, {class: "tile neighbour",
                              neighbour: neighbour,
                              neighbour_colour: neighbourColour(neighbour, num_algos),
                              x: "" + i,
                              y: "" + 0} , false);
        } else if ((multiplayer) && (i < boardwidth)) {
            var neighbour = (num_algos + ((num_algos + 3) % num_algos) - 1) % num_algos;
            addCell(col_tag, {class: "tile neighbour",
                              neighbour: neighbour,
                              neighbour_colour: neighbourColour(neighbour, num_algos),
                              x: "" + (boardwidth + i),
                              y: "" + 0} , false);
        } else {
            addTile(col_tag, {class: "tile"});
        }

        for(var j=boardheight-1; j>=0; --j) {
            if (multiplayer && (i < 0)) {
                var neighbour = (num_algos - 1) % num_algos;
                addCell(col_tag, {class: "tile neighbour",
                                  neighbour: neighbour,
                                  neighbour_colour: neighbourColour(neighbour, num_algos),
                                  x: "" + (boardwidth + i),
                                  y: "" + j} , false);
            } else if (multiplayer && (i >= boardwidth)) {
                var neighbour = (num_algos + 1) % num_algos;
                addCell(col_tag, {class: "tile neighbour",
                                  neighbour: neighbour,
                                  neighbour_colour: neighbourColour(neighbour, num_algos),
                                  x: "" + (i - boardwidth),
                                  y: "" + j} , false);
            } else if ((i < 0) || (i >= boardwidth)){
                addTile(col_tag, {class: "tile"});
            } else {
                addCell(col_tag, {class: "tile sky",
                                  x: "" + i,
                                  y: "" + j} , true);
            }
        }
        
        if (multiplayer && (i >= 0) && (i < boardwidth)) {
            var neighbour = (2 * num_algos - 3) % num_algos;
            addCell(col_tag, {class: "tile neighbour",
                              neighbour: neighbour,
                              neighbour_colour: neighbourColour(neighbour, num_algos),
                              x: "" + i,
                              y: "" + (boardheight -1)} , false);
        } else if (multiplayer && (i >= boardwidth)) {
            var neighbour = (num_algos + ((2 * num_algos - 3) % num_algos) + 1) % num_algos;
            addCell(col_tag, {class: "tile neighbour",
                              neighbour: neighbour,
                              neighbour_colour: neighbourColour(neighbour, num_algos),
                              x: "" + (i - boardwidth),
                              y: "" + (boardheight - 1)} , false);
        } else {
            addTile(col_tag, {class: "tile"});
        }
    }
    
    $("#board .tile>.bee.layer").attr("volant_id", "").attr("heading", "").attr("energy", "").attr("nectar", "");
    $("#board .tile>.seed.layer").attr("volant_id", "").attr("heading", "");
}

function gameOver(game, msg) {
    handleEndOfGame("#gameover", game, msg);
}

function abortGame(game, msg) {
    handleEndOfGame("#error", game, msg);
}

function handleEndOfGame(dialog, game, msg) {
    $(dialog).text(msg);
    
    onGameOver(game);
    
    $(dialog).dialog("open");
}

function errorMessage(msg) {
    $("#error").text(msg);
    $(".current-player").removeClass("current-player");
    $("#error").dialog("open");
}

function setBees(bees, clazz) {
    $("#board ." + clazz + ">.bee.layer[volant_id!='']").attr("volant_id", "").attr("heading", "").attr("energy", "").attr("nectar", "").attr("type", "");
    
    $("." + clazz + ">.bee.layer>.ometer").css('visibility', 'hidden');
    $("." + clazz + ">.bee.layer>.ometer>.bar.ok").removeClass("ok");
    $("." + clazz + ">.bee.layer>.ometer>.bar.medium").removeClass("medium");
    $("." + clazz + ">.bee.layer>.ometer>.bar.low").removeClass("low");

    $.each(bees, function(bee_id, bee_details) {
        var type = bee_details[0];
        var x = bee_details[1];
        var y = bee_details[2];
        var heading = bee_details[3];
        if (type=="Bee" || type=="QueenBee") {
            var energy = bee_details[4];
            var nectar = bee_details[6];
        
            var bee = $("." + clazz + "[x=" + x +"][y=" + y + "]>.bee");
            bee.attr("volant_id", bee_id).attr("heading", heading).attr("energy", energy).attr("nectar", nectar).attr("type", type);
            bee.children(".ometer").css('visibility', 'visible');
            var bar = bee.children(".ometer").children(".bar").css("width", Math.min(energy/2, 20) + "pt");
            if (energy<10) {
                bar.addClass("low");
            } else if (energy<20) {
                bar.addClass("medium");
            } else {
                bar.addClass("ok");
            }
        }
    });
}

function setSeeds(seeds, clazz) {
    $("#board ." + clazz + ">.seed.layer[volant_id!='']").attr("volant_id", "").attr("heading", "");

    $.each(seeds, function(volant_id, seed_details) {
        var type = seed_details[0];
        var x = seed_details[1];
        var y = seed_details[2];
        var heading = seed_details[3];
        if (type=="Seed") {
            var seed = $("." + clazz + "[x=" + x +"][y=" + y + "]>.seed");
            seed.attr("volant_id", volant_id).attr("heading", heading);
        }
    });
}

function setCrashesOfType(crashType, crashes, clazz) {
    $.each(crashes, function(volant_id, volant_details) {
        var x = volant_details[1];
        var y = volant_details[2];
        var heading = volant_details[3];
        $("." + clazz + "[x=" + x +"][y=" + y + "]>.crash.layer").attr("crash_type", crashType).attr("heading", heading);
    });
}

function setCrashes(crashes, clazz) {
    $("#board ." + clazz + ">.crash.layer[crash_type!='']").attr("crash_type", "").attr("heading", "");

    setCrashesOfType("exhausted", crashes.exhausted, clazz);
    setCrashesOfType("collided", crashes.collided, clazz);
    setCrashesOfType("headon", crashes.headon, clazz);
    setCrashesOfType("seeds", crashes.seeds, clazz);
}

function setLandings(landings, clazz) {
    $("#board ." + clazz + ">.landed").removeClass("landed");

    $.each(landings, function(volant_id, volant_details) {
        var x = volant_details[1];
        var y = volant_details[2];
        $("." + clazz + "[x=" + x +"][y=" + y + "]>.scenary").addClass("landed");
    });
}

function setHives(hives, clazz) {
    $("#board ." + clazz + ">.scenary.hive>.ometer").css('visibility', 'hidden');
    $("#board ." + clazz + ">.scenary.hive").removeClass("hive");
    
    $.each(hives, function(i, hive) {
        var x = hive[0];
        var y = hive[1];
        var nectar = hive[2];
        $("." + clazz + "[x=" + x +"][y=" + y + "]>.scenary").addClass("hive");
        $("." + clazz + "[x=" + x +"][y=" + y + "]>.scenary.hive>.ometer").css('visibility', 'visible').children('.bar').css("width", Math.min(nectar/5, 20) + "pt");
    });
}

function setFlowers(flowers, turnNum, clazz) {  
    $("#board ." + clazz + ">.scenary.flower").removeClass("flower").attr("size", "").removeClass("dead");
    
    $.each(flowers, function(i, flower) {
        var x = flower[0];
        var y = flower[1];
        var potency = flower[3];
        var flwr = $("." + clazz + "[x=" + x +"][y=" + y + "]>.scenary").addClass("flower").attr("potency", potency);
        if ((flower[5] - 10) < turnNum) {
            flwr.addClass("dead");
        }
    });
}


var PENDING = "pending";

var recievedMoves = null;


function resetMoves(game) {
    recievedMoves = []
    for (i = 0; i < game.state.boards.length; i++) { 
        recievedMoves.push(PENDING);
    }
}

function applyMove(i, game, move) {
    recievedMoves[i] = move;
    
    for (i = 0; i < recievedMoves.length; i++) { 
        if (recievedMoves[i]==PENDING) {
            return;
        }
    }
    
    applyMoves(game, recievedMoves);
}

function writeStateToBoard(game, board, clazz) {
    // Write the bees back to the board
    setBees(game.state.boards[board].inflight, clazz);
    
    // Write the seeds back to the board
    setSeeds(game.state.boards[board].inflight, clazz);
    
    // Update the hives
    setHives(game.state.boards[board].hives, clazz);
    
    // Update the flowers
    setFlowers(game.state.boards[board].flowers, game.state.turnNum, clazz);

    // Write the crashes to the board
    setCrashes(game.crashed[board], clazz);

    // Write the landings to the board
    setLandings(game.landed[board], clazz);
}

function applyMoves(game, moves)  {
    $(".sky").unbind("click", showControls);

    take_turn(game.state, moves, function(response) {
        game.state = response.state;
        game.received = response.received;
        game.lost = response.lost;
        game.crashed = response.crashed;
        game.landed = response.landed;
    
        writeStateToBoard(game, 0, "sky");
        
        for (var board=0; board<game.state.boards.length; board++) {
            writeStateToBoard(game, board, "neighbour[neighbour=" + board + "]");
        }
        
        // Loop!
        next_move(game);
    });
}

function hideControls() {
    $(".sky>.layer>.controls").css('visibility', 'hidden');
    $(".sky.selected").removeClass("selected");
}

function showControls(event){
    hideControls();
    var tile = $(event.target).parent()
    
    var bees_to_control = tile.children('.bee.layer[heading!=""]')
    bees_to_control.parent().addClass("selected");
    bees_to_control.children('.controls').css('visibility', 'visible');

    var seeds_to_control = tile.children('.seed.layer[heading!=""]')
    seeds_to_control.parent().addClass("selected");
    seeds_to_control.children('.controls').css('visibility', 'visible');
}

function requestMoves(game) {
    resetMoves(game);
    
    var boards = [];
    var algos = [];
    var human_input_required = false;
    for (i = 0; i < game.state.boards.length; i++) {
        if (game.algos[i] == "Human") {
            human_input_required = true;
        } else {
            boards.push(i);
            algos.push(game.algos[i]);
        }
    }
    
    var minimum_time = 0.5;
    if ($("#turbo").is(':checked')) {
        minimum_time = 0;
    } 

    if (boards.length > 0) {
        $.ajax("/move",
        {type: "POST",
        data: JSON.stringify($.extend({minimumTime:minimum_time}, {boards: boards,
                                                                   algos: algos,
                                                                   state: game.state,
                                                                   crashed: game.crashed,
                                                                   lost: game.lost,
                                                                   received: game.received,
                                                                   landed: game.landed})),
        cache: false,
        crossDomain: false,
        contentType: "application/json; charset=utf-8",
        dataType: "json"
        }).done(function(data, textStatus, jqXHR)
        {
            if ("error" in data) {
                abortGame(game, data.error);
            } else {
                for (i = 0; i < boards.length; i++) {
                    applyMove(boards[i], game, data.ok[i]);
                }
            }
        }).fail(function(jqXHR, textStatus, errorThrown) 
        {
            abortGame(game, textStatus + ' ' + errorThrown);
        });
    }
    
    if (human_input_required) {
        if (Object.keys(game.state.boards[0].inflight).length>0) {
            $("#human-input").show();
            $(".sky").click(showControls);
        } else if ((boards.length == 0) && (minimum_time > 0)) {
            setTimeout(function () {
                applyMove(0, game, null);
            }, minimum_time * 1000);
        } else {
            applyMove(0, game, null);
        }
    }
}

function onGameOver(game) {
    var boards = [];
    var algos = [];
    for (var i = 0; i < game.state.boards.length; i++) {
        if (game.algos[i] != "Human") {
            boards.push(i);
            algos.push(game.algos[i]);
        }
    } 
    
    if (boards.length > 0) {
        $.ajax("/gameover",
        {type: "POST",
        data: JSON.stringify({state: game.state,
                              boards: boards,
                              algos: algos,
                              crashed: game.crashed,
                              lost: game.lost,
                              received: game.received,
                              landed: game.landed}),
        cache: false,
        crossDomain: false,
        contentType: "application/json; charset=utf-8",
        dataType: "json"
        }).done(function(data, textStatus, jqXHR)
        {
            if ("error" in data) {
                console.log("Error sending game over message: " + data.error);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) 
        {
            console.log("Error sending game over message: " + textStatus + ' ' + errorThrown);
        });
    }
}

function onGameStart(game, callback) {
    var boards = [];
    var algos = [];
    for (i = 0; i < game.state.boards.length; i++) {
        if (game.algos[i] != "Human") {
            boards.push(i);
            algos.push(game.algos[i]);
        }
    } 
    
    if (boards.length > 0) {
        $.ajax("/startgame",
        {type: "POST",
        data: JSON.stringify({ boards: boards, algos: algos, state: game.state}),
        cache: false,
        crossDomain: false,
        contentType: "application/json; charset=utf-8",
        dataType: "json"
        }).done(function(data, textStatus, jqXHR)
        {
            if ("error" in data) {
                console.log("Error sending game start message: " + data.error);
            } else {
                callback(data.ok);
            }
        }).fail(function(jqXHR, textStatus, errorThrown) 
        {
            console.log("Error sending game start message: " + textStatus + ' ' + errorThrown);
        });
    } else {
        callback();
    }
}

function take_turn(gameState, moves, callback) {
    $.ajax("/turn",
    {type: "POST",
    data: JSON.stringify($.extend({commands: moves}, gameState)),
    cache: false,
    crossDomain: false,
    contentType: "application/json; charset=utf-8",
    dataType: "json"
    }).done(function(data, textStatus, jqXHR)
    {
        if ("error" in data) {
            console.log("Error taking turn: " + data.error);
        } else {
            callback(data.ok);
        }
    }).fail(function(jqXHR, textStatus, errorThrown) 
    {
        console.log("Error taking turn: " + textStatus + ' ' + errorThrown);
    });
}


function setTextAndHighlightChange(element, value) {
    if (element.text() == value) {
        element.removeClass("changed");
    } else {
        element.text(value).addClass("changed");
    }
}


function displayScore(game) {
    if (game.state.boards.length > 1) {
        $("#multiscoreboard table tr").remove();
        
        var num_algos = game.state.boards.length;
        for(var i=0; i<num_algos; i++) {
            var row = $('<tr/>').appendTo("#multiscoreboard table");
            $('<td/>', {class: "neighbour", neighbour_colour: neighbourColour(i, num_algos)}
              ).text(game.algos[i]).appendTo(row);
            $('<td>' + game.state.boards[i].score + '</td>').appendTo(row);
        }
        
        $("#multiscoreboard").show();
    } else {
        $("#multiscoreboard").hide();
    }

    $("#turn").text(game.state.turnNum);
    $("#score").text(game.state.boards[0].score);
    setTextAndHighlightChange($("#ndeadbees"), game.state.boards[0].deadbees);
    setTextAndHighlightChange($("#pdeadbees"), game.state.boards[0].deadbees * -3);
    setTextAndHighlightChange($("#nhives"), game.state.boards[0].hives.length);
    setTextAndHighlightChange($("#phives"), game.state.boards[0].hives.length * 100);
    setTextAndHighlightChange($("#nflowers"), game.state.boards[0].flowers.length);
    setTextAndHighlightChange($("#pflowers"), game.state.boards[0].flowers.length * 50);
    var nectar = 0;
    $.each(game.state.boards[0].hives, function(i, hive) {
       nectar += hive[2];
    });
    setTextAndHighlightChange($("#nnectar"), nectar);
    setTextAndHighlightChange($("#pnectar"), nectar * 2);
}

function isGameOver(game) {
    return game.state.turnNum >= game.state.gameLength;
}

function next_move(game) {
    displayScore(game);

    if (isGameOver(game)) {
        if (game.state.boards.length==1) {
            gameOver(game, "You scored " + game.state.boards[0].score);
        } else {
            var winner = -1;
            for (var i=0; i<game.state.boards.length; i++) {
                if ((winner < 0) || (game.state.boards[i].score > game.state.boards[winner].score)) {
                    winner = i;
                }
            }
            
            var winners = [];
            var human_won = false;
            for (var i=0; i<game.state.boards.length; i++) {
                if (game.state.boards[i].score == game.state.boards[winner].score) {
                    winners.push(game.algos[i]);
                    if (game.algos[i]=="Human") {
                        human_won = True;
                    }
                }
            }

            if (winners.length > 1) {
                if (human_won) {
                    gameOver(game, "You are joint first with " + (winners.length - 1) + " others.");
                } else {
                    gameOver(game, winners.length + "joint winners.");
                }
            } else {
                if (human_won) {
                    gameOver(game, "You Won!!");
                } else {
                    gameOver(game, winners[0] + " Wins!!");
                }
            }
        }
    } else {
        requestMoves(game);
    }
}

function listAlgos() {
    var algos = [$("#player1_algo option:selected").text()]
    if ($("#multiplayer").is(':checked')) {
        $("#player1_algo option").each(function () {
            if ((this.text != algos[0]) && (this.text != "Human")) {
                algos.push(this.text);
            }
        });
    }
    return algos;
}

function start() {
    var algos = listAlgos();
    
    $("#algoname").text(algos[0]);
    
    $.ajax("/newgame", {
        type: "POST",
        data: JSON.stringify({
            boards: algos.length,
            boardWidth: parseInt($("#boardwidth")[0].value),
            boardHeight: parseInt($("#boardheight")[0].value),
            moves: parseInt($("#nmoves")[0].value),
            hives: 1,
            flowers: 1
        }),
        cache: false,
        crossDomain: false,
        contentType: "application/json; charset=utf-8",
        dataType: "json"
    }).done(function(data, textStatus, jqXHR) {
        if ("error" in data) {
            errorMessage(data.error);
        } else {
            game = data.ok;
            game.algos = algos;
            setHives(game.state.boards[0].hives);
            setFlowers(game.state.boards[0].flowers, game.state.turnNum);
            setBees(game.state.boards[0].inflight, "sky");
            onGameStart(game, function() {
                next_move(game);
            });
        }
    }).fail(function(jqXHR, textStatus, errorThrown) 
    {
        errorMessage(textStatus + ' ' + errorThrown);
    });
}

function onClickStart() {
    drawBoard();
    $("#newgame").dialog("close");
    start();
}

function setToolTip() {
    $(this).attr('title', $(this).val());
}

function loadAlgoList() {
    $.ajax("/algos", { type: "GET",
                       cache: false,
                         crossDomain: false,
                       dataType: "json" }
    ).done(function(data, textStatus, jqXHR) {
        if ("error" in data) {
            alert("Error reading list of available algos.");
            console.log(data.error);
        } else {
            $.each(data.ok, function(key, value) {
                $("#player1_algo").append($('<option>', { value : value }).text(key)); 
            });
            $("#player1_algo")[0].options[1].selected = true;
            $(".settings select").each(setToolTip);
        }
    }).fail(function(jqXHR, textStatus, errorThrown) 
    {
        alert("Error reading list of available algos.");
        console.log(textStatus);
        console.log(errorThrown);
    });
}

$(function () {

    drawBoard();
    
    $("#infopopup").dialog({width: "60%",
                            modal: true,
                            autoOpen:false,
                            buttons: [ { text: "OK", click: function() { $( this ).dialog( "close" ); }, autofocus:true },     ]
                            });

    $("#info").click(function(){
        $("#infopopup").dialog("open");
    });
        
    $("#exitpopup").dialog({width: "250px",
                            modal: true,
                            autoOpen:false,
                            buttons: [ { text: "No", click: function() { $( this ).dialog( "close" ); }, autofocus:true },
                                       { text: "Yes", click: function() { location.reload();  }},     ]
                            });
    
    $("#exit").click(function(){
        $("#exitpopup").dialog("open");
    });
    
    $("#gameover").dialog({width: "250px",
                         modal: true,
                           autoOpen:false,
                         buttons: [ { text: "New Game", click: function() {
                                    $("#newgame").dialog("open");
                                    $(this).dialog("close");
                                }},     ]
                        });
    
    $("#error").dialog({width: "90%",
                         modal: true,
                           autoOpen:false,
                         buttons: [ { text: "New Game", click: function() {
                                    $("#newgame").dialog("open");
                                    $(this).dialog("close");
                                }},     ]
                        });
    
    $("#newgame").dialog({width: "400px",
                          modal: true,
                          buttons: [ { text: "Help", click: function() { $("#infopopup").dialog("open"); } },
                                     { text: "Start", click: onClickStart, autofocus:true }, ]
                        });
                        
    $('.ui-dialog-titlebar-close').hide();
    
    $(".settings select").change(setToolTip).change(drawBoard);
    
    // Because IE doesn't provide a spinner
    $("#boardwidth").spinner({ change: drawBoard,
                               stop: drawBoard });

    $("#boardheight").spinner({ change: drawBoard,
                                stop: drawBoard });

    $("#multiplayer").click(drawBoard);

    $("#nmoves").spinner();
    
    $("#multiscoreboard").hide();
    
    $("#human-skip").click(function() {
        applyMove(0, game, null);
        $("#human-input").hide();
        hideControls();
    });

    loadAlgoList();
});
