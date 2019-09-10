#!/usr/bin/perl -w
use strict;
use FindBin qw($Bin);
use File::Spec::Functions qw(:ALL);
# Use local CPAN
use lib ($Bin, catdir($Bin, '..', 'dependencies', 'CPAN') );


use Diogenes::Base;
use CGI qw(:standard);
use CGI::Carp 'fatalsToBrowser';
$| = 1;

use constant is_win32  => 0 <= index $^O, "Win32";

BEGIN {
   if ( is_win32 ) {
      eval "use Win32::ShellQuote qw(quote_native); 1" or die $@;
   }
}


my $q = $Diogenes_Daemon::params ? new CGI($Diogenes_Daemon::params) : new CGI;
print $q->header(-type=>"text/html; charset=utf-8");

my $d = new Diogenes::Base(-type => 'none');
my $tll_path = $d->{tll_pdf_dir};

print $q->h2('Downloading PDFs of the <i>Thesaurus Linguae Latinae</i>.'),
    $q->p("This can take a while. Close this window to interrupt download. Destination folder: $tll_path");

# {
#     local @ARGV = [$tll_path];
#     do 'tll-pdf-download.pl';
# }

# my $script = File::Spec->catfile($Bin, 'tll-pdf-download.pl');
# system($^X, $script, $tll_path);

my @cmd;
push @cmd, $^X;
push @cmd, File::Spec->catfile($Bin, 'tll-pdf-download.pl');
push @cmd, $tll_path;

my ($command, $fh);
if (is_win32) {
    $command = quote_native(@cmd);
    open ($fh, '-|', $command) or die "Cannot exec $command: $!";
}
else {
    open ($fh, '-|', @cmd) or die "Cannot exec: "
        . (join ' ', @cmd) . ": $!";
}
# print $f->p("Command: $command \n");
$fh->autoflush(1);
print '<pre>';
{
    local $/ = "\n";
    print $_ while (<$fh>);
}
print '</pre>';

print $q->h3('Finished Downloading.');


