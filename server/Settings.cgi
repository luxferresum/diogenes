#!/usr/bin/perl -w
use strict;
use FindBin qw($Bin);
use File::Spec::Functions qw(:ALL);
# Use local CPAN
use lib ($Bin, catdir($Bin, '..', 'dependencies', 'CPAN') );

use Diogenes::Base;
use CGI qw(:standard);
use CGI::Carp 'fatalsToBrowser';
use Data::Dumper;    
use Cwd;
use File::Spec;
$| = 1;

my $q = $Diogenes_Daemon::params ? new CGI($Diogenes_Daemon::params) : new CGI;

print $q->header(-type=>"text/html; charset=utf-8");
my $d = new Diogenes::Base(-type => 'none');

my $rcfile = $d->{auto_config};
my $config_file = $d->{user_config};

my @fields = qw(context cgi_default_encoding perseus_show browse_lines
                input_encoding tlg_dir phi_dir ddp_dir) ;

my %perseus_labels = (popup => "Pop up a new window",
                      split => "Split window",
                      newpage => "Show in new page",
                      full => "Show in same page");

my $begin_comment = "
## This file is automatically generated -- do not edit it by hand.
## Instead, use a file called diogenes.config in this directory to
## record configuration options that will not be overwritten or
## overridden by these settings. \n";

my $perl_ver = sprintf "%vd\n", $^V;
my $xulrunner_ver = $ENV{'Xulrunner-version'};

my $version_info = 
"Diogenes version: $Diogenes::Base::Version
<br>Perl version: $perl_ver";
if ($xulrunner_ver) {
    $version_info .= "<br>Xulrunner (Mozilla) version: $xulrunner_ver";
}
$version_info .= '<br>Operating System: '. $^O;

my $display_splash = sub
{

    print $q->start_html(-title=>'Diogenes Settings Page',
                         -bgcolor=>'#FFFFFF'), 
    $q->start_form,
    '<center>',
    $q->h1('Your Diogenes Settings'),

#         $q->h2('You can change some of your settings here:'),
        $q->table
        (
         $q->Tr
         (
          $q->th({align=>'right'}, 'Greek input mode:'),
          $q->td($q->popup_menu(-name=>'input_encoding',
                                -Values=>['Unicode', 'Perseus-style', 'BETA code'],
                                -Default=>$d->{input_encoding}))
         ),
         $q->Tr
         (
          $q->th({align=>'right'}, 'Greek output encoding:'),
          $q->td($q->popup_menu(-name=>'cgi_default_encoding',
                                -Values=>[$d->get_encodings],
                                -Default=>$d->{cgi_default_encoding}))
         ),
         $q->Tr
         (
          $q->th({align=>'right'}, 'How to present Perseus data:'),
          $q->td($q->popup_menu(-name=>'perseus_show',
                                -values=>[keys %perseus_labels],
                                -labels=>\%perseus_labels,
                                -default=>$d->{perseus_show}))
         ),
         $q->Tr
         (
          $q->th({align=>'right'}, 'Amount of context to show in searches:'),
          $q->td($q->popup_menu(-name=>'context',
                                -Values=>\@Diogenes::Base::contexts,
                                -Default=>$d->{context}))
         ),
         $q->Tr
         (
          $q->th({align=>'right'}, 'Number of lines to show in browser:'),
          $q->td($q->popup_menu(-name=>'browse_lines',
                                -Values=>[$d->{browse_lines}, 1..4, map {$_ * 5} (1 .. 20)],
                                -Default=>$d->{browse_lines}))
         ),
         $q->Tr
         (
          $q->th({align=>'right'}, 'The location of the TLG database:'),
          $q->td($q->textfield( -name=>'tlg_dir',
                                -size=>40,
                                -maxlength=>100,
                                -Default=>$d->{tlg_dir}))
         ),
         $q->Tr
         (
          $q->th({align=>'right'}, 'The location of the PHI database:'),
          $q->td($q->textfield( -name=>'phi_dir',
                                -size=>40,
                                -maxlength=>100,
                                -Default=>$d->{phi_dir}))
         ),
         $q->Tr
         (
          $q->th({align=>'right'}, 'The location of the DDP database:'),
          $q->td($q->textfield( -name=>'ddp_dir',
                                -size=>40,
                                -maxlength=>100,
                                -Default=>$d->{ddp_dir}))
         ),
        ),
          $q->p('To enable new settings, click below'),
          $q->table($q->Tr($q->td(
                               $q->submit(-Value=>'Save these settings',
                                          -name=>'Write'),
                           )));
    # Don't suggest that remote users edit server config files
    if ($ENV{'Diogenes_Config_Dir'}) {
        print
            $q->hr,
            $q->h2('For experts'),
            $q->p('A number of other, more obscure settings for Diogenes can be specified.
You can add these manually to a configuration file: ', 
                  "<br> $config_file <br> To view all settings currently in effect, click here."),
            $q->table($q->Tr($q->td(
                                 $q->submit(-Value=>'Show all current settings',
                                            -name=>'Show'),
                             )));
    }
    print
        $q->hr,
        $q->h2('Version information'),
        $q->p($version_info),
        

          '</center>',
          $q->end_form,
          $q->end_html;                  
};

my $display_current = sub
{
    print '<html><head><title>Diogenes Settings</title></head>
	 <body>';
    
    print '<h3>Current configuration settings for Diogenes:</h3>';
    
    my $init = new Diogenes::Base(type => 'none');
    my $dump = Data::Dumper->new([$init], [qw(Diogenes Object)]);
    $dump->Quotekeys(0);
    $dump->Maxdepth(1);
    my $out = $dump->Dump;
    
    $out=~s/&/&amp;/g;
    $out=~s/\"/&quot;/g;
    $out=~s/>/&gt;/g;
    $out=~s/</&lt;/g;                            
    
    my @out = split /\n/, $out;
    $out[0] = $out[-1] = '';
    
    print '<pre>';
    print (join "\n", sort @out);
    print '</pre></body></html>';
};

my $write_changes = sub
{

    my $file = $begin_comment;
    for my $field (@fields)
    {	
        $file .= "$field ".'"'.$q->param($field).'"'."\n";
    }
    
    open RC, ">$rcfile" or die "Can't open $rcfile: $!\n";
    print RC $file;
    close RC or die "Can't close $rcfile: $!\n";

    print $q->start_html(-title=>'Settings confirmed',
                         -bgcolor=>'#FFFFFF'), 
    $q->center(
        $q->h1('Settings changed'),
        $q->p("Your new settings are now in effect, and have been written to this file:<br>$rcfile"),
        $q->p('You may now close this window.')),
    $q->end_html;                  
};


if ($q->param('Show'))
{
    $display_current->();
}
elsif ($q->param('Write'))
{
    $write_changes->();
}
else
{
    $display_splash->();
}

