tinymce.init({
    //选择class为content的标签作为编辑器
    selector: '#rich_content',
    //方向从左到右
    directionality: 'ltr',
    //语言选择中文
    language: 'zh_CN',
    //高度为400
    height: 400,
    width: '100%',

    menubar: false,

    //工具栏上面的补丁按钮
    plugins: [
        'advlist autolink link lists charmap preview hr anchor pagebreak',
        'searchreplace wordcount visualblocks visualchars code fullscreen insertdatetime media nonbreaking',
        'save contextmenu directionality template paste textcolor',
        'codesample imageupload',
        'code paste',
    ],
    //工具栏的补丁按钮
    toolbar: 'undo redo | imageupload | styleselect bold italic fontsizeselect forecolor |\
     alignleft aligncenter alignjustify numlist | image link codesample | preview | fullscreen',
    //字体大小
    fontsize_formats: '10pt 12pt 14pt 18pt 24pt 36pt',
    //按tab不换行
    nonbreaking_force_tab: true,
    imageupload_url: "submit-image",
    paste_data_images: true,
});
