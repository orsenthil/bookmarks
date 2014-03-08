%fontsize_min = 8
%fontsize_max = 24

<h3>Years cloud</h3>
<div id="years_cloud">
    %count_min = 1
    %count_max = max([v[1] for v in yf]) if yf else 10
    %for year, x in yf:
      %size = (fontsize_max-fontsize_min)*(x-count_min)/(count_max-count_min or 1) + fontsize_min
      <a href="/search/year:{{year}}" style="font-size: {{int(size)}}pt">{{year}}</a>&nbsp;&nbsp;
    %end
  %end
</div>
