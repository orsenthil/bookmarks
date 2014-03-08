%fontsize_min = 8
%fontsize_max = 24

<h3>Tags cloud</h3>
<div id="tags_cloud">
    %count_min = 1
    %count_max = max([v[1] for v in tf]) if tf else 10
    %for tag, x in tf:
      %size = (fontsize_max-fontsize_min)*(x-count_min)/(count_max-count_min or 1) + fontsize_min
      %stag = '"{}"'.format(tag) if ' ' in tag else tag
    <a href="{{('/search/tag:'+stag)}}" style="font-size: {{int(size)}}pt">{{tag}}</a>&nbsp;&nbsp;
    %end
</div>
