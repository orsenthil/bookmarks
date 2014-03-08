<br/>
<div class="hdr">
  <span class="label">Search:</span>
  <span class="num_wrapper"><span class="nbookmarks">{{len(bks)}}</span> bookmarks</span>
  <div class="wrapper"><span class="sterm">{{sterm or "none"}}</span><input type="text" class="sterm"/></div>
</div>
<br/><br/>

<ul>
  %for b in bks:
  <li class="bookmark">
    <span class="btns">
      <img src="/img/edit.png" class="btn_edit"/>
      &nbsp;&nbsp;
      <img src="/img/delete.png" class="btn_remove"/>
    </span>
    <div class="title">{{b.title}}</div>
    <div>
      %tags_str = ', '.join(['<a href="/search/tag:\''+ tag +'\'" class="tag">'+tag+'</a>' for tag in sorted(b.tags)])
      <b>Tags: </b><span class="tags">{{!tags_str}}</span>
      &nbsp;&nbsp;&nbsp;
      <b>Added: </b><span class="added">{{b.added}}</span>
    </div>
    <div><a class="url" href="{{b.url}}" target="_blank">{{b.url}}</a></div>
  </li>
  %end
</ul>

<script>show_bookmarks();</script>

%rebase layout title='Show results'
