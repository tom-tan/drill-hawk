var current_workflow_id = '';
var initStackedBarChart = {
  draw: function(config) {
    me = this,
    domEle = config.element,
    stackKey = config.key,
    data = config.data,
    margin = {top: 20, right: 20, bottom: 30, left: 180}, // left is title width

    //
    // 全体設定
    //
    // グラフ領域の計算
    width = 960 - margin.left - margin.right,
    height = 500 - margin.top - margin.bottom,

    //
    // X,Y軸のスケール設定
    //
    xScale = d3.scaleLinear().rangeRound([0, width]),
    yScale = d3.scaleBand().rangeRound([height, 0]).padding(0.1),

    color = d3.scaleOrdinal(d3.schemeCategory20),

    //
    // グラフ本体
    //
    svg = d3.select("#"+domEle).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    // 積み重ねグラフの設定
    var stack = d3.stack()
      .keys(stackKey)
      .offset(d3.stackOffsetNone);
  
    // tooltip
    var tooltip = d3.select("body").append("div").attr("class", "tooltip");

    var layers = stack(data);

    // データ数からY軸の個数を計算
    yScale.domain(data.map(function(d) {
      var key = d.workflow_id;
      var yscale_title = key;
      return yscale_title;
    }));
    // 積み重ね値からX軸の最大値を計算
    xScale.domain([0, d3.max(layers[layers.length - 1], function(d) { return d[1]; }) ]).nice();

    // グラフを1ブロック毎描画
    var layer = svg.selectAll(".layer")
      .data(layers)
      .enter().append("g")
      .attr("class", "layer")
      .style("fill", function(d, i) { return color(i); });

    var title = layer.selectAll("rect")
        .data(function(d) { return d; });

    layer.on("mouseover", function(d) {

      var index = get_workflow_index(d);
      var key = d.key.replace(/^time-/, '');
      key = key.replace(/^cost-/, '');
      var cost = Math.floor(d[w].data['cost-' + key]*100)/100;
      var time = d[w].data['time-' + key];
      var container_id = d[w].data['id-' + key];
      var instance_type = d[w].data['itype-' + key];
      var from_datetime = d[w].data['start-' + key].substring(0, 19);
      var to_datetime = d[w].data['end-' + key].substring(0, 19);
      tooltip
        .style("visibility", "visible")
        .html(
              "<div class='btn btn-sm btn-warning'>" + d[w].data['workflow_name'] + "</div>"
              + "<br><span class='title'>name :</span> "
              + "<span class='value'>" + key + "</span>"

              // instance_type
              + "<br><span class='title'>instance_type :</span>"
              + "<span class='value'>" + instance_type + "</span>" 

              // cost
              + "<br><span class='title'>fee :</span>"
              + "<span class='value'>" + cost
              + " usd</span>"
              // time
              + "<br><span class='title'>time :</span>"
              + "<span class='value'>" + parseInt(time)
              + " sec</span>"

              + "<br><span class='title'>container_id :</span> "
              // container id: first 12 bytes
              + "<span class='value'>" + container_id.substr(0, 12) + "</span>"
              + "<br><span class='title'>from :</span> "
              + "<span class='value'>" + from_datetime + "</span>"
              + "<br><span class='title'>to :</span> "
              + "<span class='value'>" + to_datetime + "</span>"
        );
    })
    .on("click", function(d) {

      var index = get_workflow_index(d);
      var key = d.key.replace(/time-/, '');
      key = key.replace(/cost-/, '');
      var value = d[index].data[d.key];
      var container_id = d[index].data['id-' + key];
      var from_datetime = d[index].data['start-' + key];
      var to_datetime = d[index].data['end-' + key];

      // kibana のurl生成
      var target_uri = template_uri;   // {{XXXX}} 入りのurl template
      target_uri = target_uri.replace(/{{container_id}}/, container_id);
      target_uri = target_uri.replace(/{{from_datetime}}/, from_datetime);
      target_uri = target_uri.replace(/{{to_datetime}}/, to_datetime);
      var url = base_url + target_uri;
      console.log(url);
      window.open(url, "kibana");

      // kibana のグラフのタイトル領域を設定
      var kibana_title = d3.select("#kibana_title");
      var title_text = '<span class="step_name">' + key + " </span> "
        + "workflow_id(" + current_workflow_id + ") container_id(" + container_id + ")";
      kibana_title.html(title_text);
    })
    .on("mousemove", function(d) {
      tooltip
        .style("top", (d3.event.pageY - 80) + "px")
        .style("left", (d3.event.pageX + 30) + "px");
    })
    .on("mouseout", function(d) {
      tooltip.style("visibility", "hidden");
      tr = $('#workflow-'+current_workflow_id)
      tr.removeClass('table-info');
    });

    title_and_anker = title.enter()
      .append("rect")
      .attr("y", function(d) {
        var key = d.data.workflow_id;
        // var yscale_title = key.substr(0, 16);
        var yscale_title = key;
        return yScale(yscale_title);
      })
      .attr("x", function(d) { return xScale(d[0]); })
      .attr("height", yScale.bandwidth())
      .attr("width", function(d) {
          return xScale(d[1]) - xScale(d[0]);
        });

    title_and_anker.on("mouseover", function(d) {
      current_workflow_id = d.data.workflow_id;
      tr = $('#workflow-'+current_workflow_id)
      tr.addClass('table-info');
    });

    // X軸の縦線(単位)
    xAxis = d3.axisBottom(xScale).ticks(10).tickSize(-height)
      .tickFormat(function (d) {
        var numberWithComma = new Intl.NumberFormat();
        return numberWithComma.format(d) + ' ' + config.unit_string;
    }),
    // Y軸の横線
    yAxis = d3.axisLeft(yScale),

    // X軸、Y軸描画
    draw_axis(xAxis, yAxis);

    // 凡例描画
    draw_legend(config);
  }
}

function draw_legend (config) {
  var legendVals = config.key;
  var color = d3.scaleOrdinal(d3.schemeCategory20);
  var svgLegned = d3.select(".legend-div").append("svg");  // 描画svg作成
     
  var legend = svgLegned.selectAll('.legends')　// 凡例の領域作成
    .data(legendVals)
    .enter()
        .append('g')
    .attr("class", "legends")
    .attr("transform", function (d, i) {
      {
        max_column = 6;
        y = 0;
        if (i >= max_column) {
          y = Math.floor(i/max_column) * 24;
        }
        return "translate(" + (((i%max_column) * 160)+20) + ", " + y + ")" // 各凡例をx方向に160px間隔で移動
      }
    });
 
  legend.append('rect') // 凡例の色付け四角
    .attr("x", 0)
    .attr("y", 0)
    .attr("width", 10)
    .attr("height", 10)
    .style("fill", function (d, i) { return color(i); }) // 色付け
 
  legend.append('text')  // 凡例の文言
    .attr("x", 20)
    .attr("y", 10)
    .text(function (d, i) { return d.replace(/^time-/, '').replace(/^cost-/, ''); })
    .attr("class", "textselected")
    .style("text-anchor", "start")
    .style("font-size", 12);
}

function draw_axis(xAxis, yAxis) {
    svg.append("g")
      .attr("class", "axis axis--x")
      .attr("transform", "translate(0," + (height+5) + ")")
      .call(xAxis);

    svg.append("g")
      .attr("class", "axis axis--y")
      .attr("transform", "translate(0,0)")
      .call(yAxis);  
}

function get_workflow_index(d) {
    // mouse 上のworkflow は、各領域のmouseoverから拾った current_workflow_id
    var workflow_id = current_workflow_id;
    for (w = 0; w < d.length; w++) {
        if (d[w].data['workflow_id'] == workflow_id) {
            index = w;
            break;
        }
    }
    return index;
}
