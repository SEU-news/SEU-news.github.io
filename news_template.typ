#let r = json("latest.json")

#let data = r.at("data")
#let due = r.at("due")

#let date = data.at("date")
#let no = data.at("no")
#let first-v = int(data.at("first-v"))
#let lecture-v = int(data.at("lecture-v"))
#let other-v = int(data.at("other-v"))
#let college-v = int(data.at("college-v"))
#let club-v = int(data.at("club-v"))

#let lecture = data.at("lecture")
#let other = data.at("other")
#let college = data.at("college")
#let club = data.at("club")

#let lecture-due = due.at("lecture")
#let other-due = due.at("other")
#let college-due = due.at("college")
#let club-due = due.at("club")


#import "@preview/tiaoma:0.3.0"
#import "@preview/wrap-it:0.1.1"

#set page(
  height: auto,
  width: 9in,
  margin: (left: 0.9in, right: 0.9in, top: 0.7in, bottom: 0.7in)
)

#let eqcolumns(n, gutter: 4%, content) = {
  layout(size => [
    #let (height,) = measure(
      block(
        width: (1/n) * size.width * (1 - float(gutter)*n), 
        content
      )
    )
    #block(
      height: height / n,
      columns(n, gutter: gutter, content)
    )
  ])
}

#let wrap(lnk, body) = wrap-it.wrap-content(
tiaoma.qrcode(lnk),
body+[\
  详见：#link(lnk)],
align: right+bottom,
column-gutter: 2em
)


// #show link: it =>{underline(stroke: (dash: "densely-dotted"), text(font: ("DejaVu Sans Mono", "Noto Sans CJK SC", "Noto Sans SC"), it))}
#show link: it =>{underline(stroke: (dash: "densely-dotted", paint: rgb(222, 130, 167, 255), thickness: 1pt), text(font: ("DejaVu Sans Mono", "Noto Sans CJK SC", "Noto Sans SC"), fill:rgb("#94004c"), it))}

#set text(font: ("New Computer Modern", "Noto Sans CJK SC", "Noto Sans SC"), size: 12pt)
#set par(first-line-indent: 0pt, leading: 0.8em)

#set heading(numbering: "1.1.1.")

#show heading: it =>{
  set text(font: ("New Computer Modern", "Noto Serif CJK SC", "Noto Serif SC"), fill: rgb(51, 0, 26, 255))
  it
}

// #show table.cell.where(x: 0): it => [
//   #show link: it => 
//   #it
  
// ]
#align(center)[
  #text(size: 2.3em, weight: "bold", font: ("Noto Serif CJK SC", "Noto Serif SC"))[南哪大专醒前消息]
]

#v(-4mm)
#line(length: 100%)

#let header-table = grid(
  columns: (20%, 60%, 20%),
  align: (left + horizon, center + horizon, right + horizon),
  [#date No. #no],
  [#emph[#set text(font: "FandolKai", size: 1.2em);"秉中持正、求新博闻。"]],
  [#text(font: ("Noto Serif CJK SC", "Noto Serif SC"), weight: "bold", size: 1.1em)[南京市栖霞区]]
)

#header-table

#line(length: 100%)
#v(-4mm)

#align(center)[
  #text(size: 2.22em, weight: "bold", font: ("Noto Serif CJK SC", "Noto Serif SC"))[活动预告]
]
#v(-4mm)


#eqcolumns(2,)[
= 订阅方式和加入编辑部
// 编辑部招聘人才，用爱发电，工作轻松，详情可联系QQ：1329527951 客服小千\
想订阅本消息或获取PDF版（便于查看超链接和往期），可加QQ群：#link("https://qm.qq.com/q/4HL41Nt3sQ")[466863272]
= 活动清单
#table(
  columns: (auto, auto, auto),
  align: (center + horizon, center + horizon, center + horizon),
  stroke: 1pt,
  [*活动*], [*截止时间*], [*刊载时间*],
  ..for e in other-due {
    if e.at("due_time") != none {
    (if e.at("link") != none {
        link(e.at("link"))[#e.at("title")]
      } else {
        e.at("title")
      }
      , [#e.at("due_time").slice(5, 10)], [#link("https://nik-nul.github.io/news/"+e.at("publish_date").slice(0, 10), e.at("publish_date").slice(5, 10))])
    }
  }
)
#v(first-v * 1em)
]
#line(length: 100%)

#eqcolumns(2)[
#for e in other {
  [= #e.at("title")]
  if (e.at("link") == none) or (("", "none", "None").contains(e.at("link"))) {
    for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }
  } else {
    wrap(e.at("link"))[#for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }]  
  }
}
#v(other-v * 1em)
]

#line(length: 100%)

#if lecture.len() != 0 or lecture-due.len() != 0 {
eqcolumns(2,)[
= 讲座
#show table.cell.where(x: 0): set text(size: 0.78em)
#show table.cell.where(x: 0, y: 0): set text(size: (1/0.78) * 1em)
#table(
  columns: (auto, auto, auto),
  align: (center + horizon, center + horizon, center + horizon),
  stroke: 1pt,
  [*活动*], [*截止时间*], [*刊载时间*],
  ..for e in lecture-due {
    if e.at("due_time") != none {
    (if e.at("link") != none {
        link(e.at("link"))[#e.at("title")]
      } else {
        e.at("title")
      }
      , [#e.at("due_time").slice(5, 10)],[#link("https://nik-nul.github.io/news/"+e.at("publish_date").slice(0, 10), e.at("publish_date").slice(5, 10))])

    }
  }
)
#for e in lecture {
  [== #e.at("title")]
  if (e.at("link") == none) or (("", "none", "None").contains(e.at("link"))) {
    for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }
  } else {
    wrap(e.at("link"))[#for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }]  
  }
}
#v(lecture-v * 1em)
]

line(length: 100%)  
}

#if college.len() != 0 or college-due.len() != 0 {
  eqcolumns(2,)[
= 院级活动
#table(
  columns: (auto, auto, auto),
  align: (center + horizon, center + horizon, center + horizon),
  stroke: 1pt,
  [*活动*], [*截止时间*], [*刊载时间*],
  ..for e in college-due {
    if e.at("due_time") != none {
    (if e.at("link") != none {
        link(e.at("link"))[#e.at("title")]
      } else {
        e.at("title")
      },
      [#e.at("due_time").slice(5, 10)], [#link("https://nik-nul.github.io/news/"+e.at("publish_date").slice(0, 10), e.at("publish_date").slice(5, 10))])

    }
  }
)

#for e in college {
  [== #e.at("title")]
  if (e.at("link") == none) or (("", "none", "None").contains(e.at("link"))) {
    for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }
  } else {
    wrap(e.at("link"))[#for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }]  
  }
}
#v(college-v * 1em)
]

line(length: 100%)
}


#if club.len() != 0 or club-due.len() != 0 {
eqcolumns(2,)[
= 社团活动

#table(
  columns: (auto, auto, auto),
  align: (center + horizon, center + horizon, center + horizon),
  stroke: 1pt,
  [*活动*], [*截止时间*], [*刊载时间*],
  ..for e in club-due {
    if e.at("due_time") != none {
    (if e.at("link") != none {
        link(e.at("link"))[#e.at("title")]
      } else {
        e.at("title")
      }
      , [#e.at("due_time").slice(5, 10)], [#link("https://nik-nul.github.io/news/"+e.at("publish_date").slice(0, 10), e.at("publish_date").slice(5, 10))])
    }
  }
)

#for e in club {
  // show link: it =>{underline(stroke: (dash: "densely-dotted"), text(font: ("DejaVu Sans Mono", "Noto Sans CJK SC", "Noto Sans SC"), fill: rgb(222, 130, 167, 255), it))}
  [== #e.at("title")]
  if (e.at("link") == none) or (("", "none", "None").contains(e.at("link"))) {
    for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }
  } else {
    wrap(e.at("link"))[#for sub in e.at("description") {
    if sub.at("type") == "text" and (sub.at("content") not in ("None",)) {sub.at("content")}
    if sub.at("type") == "link" {link(sub.at("content"))}
  }]  
  }
}
#v(club-v * 1em)
]
line(length: 100%)

}
