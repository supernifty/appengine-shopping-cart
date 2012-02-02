var supernifty = function() {
  function sortNumeric(a,b) {
    return a-b;
  }

  function toNumber(arr) {
    for ( var i = 0; i < arr.length; i++ ) {
      arr[i] = parseFloat( arr[i] );
    }
  }

  function ccy_success(data) {
    var 
      target = document.getElementById("ccy_data"),
      currencies = $.parseJSON( data ),
      list = currencies['estimatedAmountTable']['currencyConversionList'][0]['currencyList']['currency'],
      map = { 'AUD': 'au', 'CAD': 'ca', 'GBP': 'gb', 'EUR': 'europeanunion' },
      result = 'Expect to pay...<br/>'; 
    for ( var i = 0; i < list.length; i++ ) {
      if ( list[i]['code'] in map ) {
        result += '<img alt="' + list[i]['code'] + '" src="/static/flags/' + map[list[i]['code']] + '.png"/> ';
      }
      result += list[i]['amount'] + ' ' + list[i]['code'] + '&nbsp;&nbsp;&nbsp;&nbsp;';
    }
    target.innerHTML = result;
  }

  function ebay_success(data) {
    var 
      target = document.getElementById("ebay_data"),
      prices = $.parseJSON( data ),
      len = prices.length,
      histogram = [],
      bucket, bucketSize, i;
    toNumber( prices );
    prices.sort( sortNumeric );
    bucketSize = ( prices[len-1] - prices[0] ) / 10;
    for ( i = 0; i < prices.length; i++ ) {
      bucket = Math.floor( ( prices[i] - prices[0] ) / bucketSize );
      if ( histogram[bucket] == undefined ) {
        histogram[bucket] = { frequency: 1, min: prices[i], max: prices[i] };
      }
      else {
        histogram[bucket].frequency += 1;
        if ( histogram[bucket].min > prices[i] ) {
          histogram[bucket].min = prices[i];
        }
        if ( histogram[bucket].max < prices[i] ) {
          histogram[bucket].max = prices[i];
        }
      }
    }
    var data = new google.visualization.DataTable();
    data.addColumn('string', 'Range');
    data.addColumn('number', 'Frequency');
    data.addRows( histogram.length );
    for ( i = 0; i < histogram.length; i++ ) {
      if ( histogram[i] == undefined ) {
        data.setValue( i, 0, 'none' );
        data.setValue( i, 1, 0 );
      }
      else {
        if ( histogram[i].min == histogram[i].max ) {
          data.setValue( i, 0, '$' + histogram[i].min );
        }
        else {
          data.setValue( i, 0, '$' + histogram[i].min + '-' + histogram[i].max );
        }
        data.setValue( i, 1, histogram[i].frequency );
      }
    }
    
    var chart = new google.visualization.BarChart( target );
    chart.draw( data, {width: 600, height: 400, title: document.getElementById("title").value, vAxis: {title: 'Price', titleTextStyle: {color: 'red'}} });

    var median = prices[Math.floor(len/2)];
    document.getElementById("price").value = median;
  }

  return {
    init: function() {
      google.load("visualization", "1", {packages:["corechart"]});
    },

    prices: function() {
      var title = document.getElementById("title").value,
        url = '/api/find/' + encodeURIComponent(title),
        target = document.getElementById("ebay_data");
      target.innerHTML = 'Please wait...';
      $.get( url, ebay_success );
    },

    currencies: function() {
      var amount = document.getElementById("amount").innerHTML,
        url = '/api/ccy/' + encodeURIComponent(amount),
        target = document.getElementById("ccy_data");
      target.innerHTML = 'Please wait...';
      $.get( url, ccy_success );
    }
  }
}();
