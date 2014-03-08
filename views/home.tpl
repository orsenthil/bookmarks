<div>
<img src="/img/add.png" class="btn_add"/>
<h1>Welcome to Bookmarks</h1>
<p>There are {{nbks}} bookmarks stored in the system, in {{ntags}} tags.</p>
</div>

<br/>
<div class="hdr">
  <span class="label">Search:</span>
  <img src="/img/search.png" class="btn_search"/>
  <div class="wrapper"><input type="text" class="sterm"/></div>
</div>

<div class="examples">Examples:&nbsp;&nbsp;
  "<tt>Bookmarks</tt>", "<tt>Bookmarks tag:python</tt>", "<tt>Bookmarks tag:python,+bottlepy,-sqlite</tt>"</div>
<br/>

%include tags_cloud tf=tf
<br/>

%include years_cloud yf=yf
<br/>

<script>main()</script>

%rebase layout title='Home'
