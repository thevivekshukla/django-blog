from django import forms






class CommentForm(forms.Form):

    content = forms.CharField(widget=forms.Textarea, label="Write here...")
    content_type = forms.CharField(widget=forms.HiddenInput)
    object_id = forms.CharField(widget=forms.HiddenInput)
