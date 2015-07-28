<script src="jsnetworkx.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/d3/3.5.5/d3.min.js" charset="utf-8"></script>
<script src="jsnetworkx.js"></script>
var jsnx = require('jsnetworkx');
var G = new jsnx.Graph();
G.addNode(1, {count: 12});
G.addNode(2, {count: 8});
G.addNode(3, {count: 15});
G.addEdgesFrom([[1,2],[2,3]]);
 
jsnx.draw(G, {
  element: '#demo-canvas',
  withLabels: true,
  nodeAttr: {
    r: function(d) {
      // `d` has the properties `node`, `data` and `G`
      return d.data.count;
    }
  }
});
