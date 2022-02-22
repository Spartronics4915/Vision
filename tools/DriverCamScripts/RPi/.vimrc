set nocompatible
set visualbell
"source $VIMRUNTIME/vimrc_example.vim
"source $VIMRUNTIME/mswin.vim
" source $HOME/darkblue.vim
syntax on
source $HOME/elflord.vim
"source $HOME/xoria256.vim
"behave mswin

"set diffexpr=MyDiff()
"function MyDiff()
"  let opt = ''
"  if &diffopt =~ 'icase' | let opt = opt . '-i ' | endif
"  if &diffopt =~ 'iwhite' | let opt = opt . '-b ' | endif
"  silent execute '!"C:\program files\Vim\vim62\diff" -a ' . opt . '"' . v:fname_in . '" "' . v:fname_new . '" > "' . v:fname_out . '"'
"endfunction

"set et
set tabstop=4
set sw=4
set softtabstop=4
filetype on
filetype plugin on
autocmd FileType c,cpp,slang set cindent tabstop=2 sw=2 softtabstop=2 noexpandtab
autocmd FileType sh set tabstop=4 sw=4 softtabstop=4 noexpandtab
autocmd FileType tcl set et tabstop=4 sw=4 softtabstop=4
autocmd FileType python set fo=croql expandtab
"set lines=60
"set columns=120
set showmatch
set hlsearch
set incsearch
colors elflord
"
" Set up the 'pastetoggle'
:map <F10> :set paste<CR>
:map <F10> :set paste<CR>
:imap <F10> <C-O>:set paste<CR>
:imap <F11> <nop>
:set pastetoggle=<F11>
"
"if &term =~ "xterm"
"  "256 color --
"  let &t_Co=256
"  " restore screen after quitting
"  set t_ti=ESC7ESC[rESC[?47h t_te=ESC[?47lESC8
"  if has("terminfo")
"    let &t_Sf="\ESC[3%p1%dm"
"    let &t_Sb="\ESC[4%p1%dm"
"  else
"    let &t_Sf="\ESC[3%dm"
"    let &t_Sb="\ESC[4%dm"
"  endif
"endif
"if has("terminfo")
"  let &t_Co=256
"  let &t_AB="\<Esc>[%?%p1%{8}%<%t%p1%{40}%+%e%p1%{92}%+%;%dm"
"  let &t_AF="\<Esc>[%?%p1%{8}%<%t%p1%{30}%+%e%p1%{82}%+%;%dm"
"else
"  let &t_Co=256
"  let &t_Sf="\<Esc>[3%dm"
"  let &t_Sb="\<Esc>[4%dm"
"endif

